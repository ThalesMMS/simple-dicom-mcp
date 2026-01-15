# Plano de Implementação: Asynchronous Operations e Storage Commitment

## Objetivo

Implementar suporte a **Asynchronous Operations Window Negotiation** e **Storage Commitment Push Model** no dicom-mcp, expandindo as capacidades do cliente DICOM para operações batch otimizadas e confirmação de armazenamento.

---

## Pré-requisitos

Antes de iniciar, verificar:
- pynetdicom >= 2.0.0 instalado
- Familiaridade com `@/Users/thales/Documents/GitHub/MCP/dicom-mcp/src/dicom_mcp/dicom_client.py`
- Familiaridade com `@/Users/thales/Documents/GitHub/MCP/dicom-mcp/src/dicom_mcp/server.py`

---

## Parte 1: Asynchronous Operations Window Negotiation

### 1.1 Objetivo
Permitir que o cliente negocie com o SCP a capacidade de enviar múltiplas requisições DIMSE simultaneamente sem aguardar resposta individual, melhorando throughput em operações batch.

### 1.2 Modificações em `dicom_client.py`

#### 1.2.1 Imports Necessários
Adicionar import de `AsynchronousOperationsWindowNegotiation` do módulo `pynetdicom.pdu_primitives`.

#### 1.2.2 Modificar `__init__` do `DicomClient`
- Adicionar parâmetro opcional `async_ops_window: int = 1` ao construtor
- Armazenar o valor em `self.async_ops_window`
- Se `async_ops_window > 1`:
  - Criar instância de `AsynchronousOperationsWindowNegotiation`
  - Configurar `maximum_number_operations_invoked` com o valor do parâmetro
  - Configurar `maximum_number_operations_performed` com o mesmo valor
  - Armazenar em `self.async_ops_negotiation`

#### 1.2.3 Criar método auxiliar `_get_extended_negotiation_items`
- Retornar lista combinando:
  - `self.storage_roles` existentes (SCP/SCU role selection)
  - `self.async_ops_negotiation` se existir
- Este método será usado em todas as chamadas de `associate()`

#### 1.2.4 Atualizar chamadas de `associate()`
Revisar todos os métodos que chamam `self.ae.associate()` e garantir que passem `ext_neg=self._get_extended_negotiation_items()` quando apropriado:
- `verify_connection` - não precisa
- `find` - não precisa (C-FIND é naturalmente sequencial)
- `move_series`, `move_study` - pode beneficiar, mas é opcional
- `_retrieve_via_c_get` - já usa ext_neg para storage_roles, combinar
- `extract_pdf_text_from_dicom` - já usa ext_neg, combinar

#### 1.2.5 Implementar método `batch_query_studies`
Novo método para queries paralelas:
- Parâmetros: lista de critérios de query, limite opcional
- Usar ThreadPoolExecutor para executar queries em paralelo
- Respeitar o window size negociado
- Retornar resultados agregados com indicação de sucesso/falha por query

### 1.3 Modificações em `server.py`

#### 1.3.1 Atualizar configuração
No arquivo de configuração (`config.py` ou modelo pydantic), adicionar campo opcional:
- `async_operations_window: int = 1`

#### 1.3.2 Passar configuração ao DicomClient
Na função `create_dicom_mcp_server`, ao criar `DicomClient`, passar o novo parâmetro se configurado.

### 1.4 Testes

#### 1.4.1 Teste unitário de negociação
- Mock de associação que aceita async ops
- Verificar que a negociação é incluída corretamente

#### 1.4.2 Teste de integração (se possível)
- Conectar a um PACS de teste que suporte async ops
- Verificar throughput melhorado em batch operations

---

## Parte 2: Storage Commitment Push Model (SCU)

### 2.1 Objetivo
Implementar cliente para solicitar confirmação de que instâncias DICOM foram armazenadas com sucesso no SCP (PACS).

### 2.2 Modificações em `dicom_client.py`

#### 2.2.1 Imports Adicionais
- `StorageCommitmentPushModel` de `pynetdicom.sop_class`
- `generate_uid` de `pydicom.uid`

#### 2.2.2 Modificar `__init__`
Adicionar `StorageCommitmentPushModel` aos requested contexts:
- `self.ae.add_requested_context(StorageCommitmentPushModel)`

#### 2.2.3 Constantes
Definir constante para o Well-Known SOP Instance UID do Storage Commitment Push Model:
- `STORAGE_COMMITMENT_PUSH_MODEL_INSTANCE = "1.2.840.10008.1.20.1.1"`

#### 2.2.4 Implementar método `request_storage_commitment`

**Parâmetros:**
- `sop_instances: List[Dict[str, str]]` - Lista de dicionários com:
  - `sop_class_uid`: UID da classe SOP da instância
  - `sop_instance_uid`: UID único da instância
- `timeout: int = 30` - Timeout em segundos para aguardar resposta

**Lógica:**
1. Gerar `TransactionUID` único usando `generate_uid()`
2. Construir Dataset para N-ACTION:
   - `TransactionUID`: o UID gerado
   - `ReferencedSOPSequence`: sequência com items contendo:
     - `ReferencedSOPClassUID`
     - `ReferencedSOPInstanceUID`
3. Criar handler para `evt.EVT_N_EVENT_REPORT`:
   - Processar `ReferencedSOPSequence` (instâncias confirmadas)
   - Processar `FailedSOPSequence` se presente (instâncias que falharam)
   - Armazenar resultados em estrutura compartilhada
4. Associar com o SCP incluindo o handler
5. Enviar N-ACTION com:
   - Action Type ID = 1 (Request Storage Commitment)
   - SOP Class UID = StorageCommitmentPushModel
   - SOP Instance UID = Well-known instance
6. Aguardar resposta do N-ACTION (aceite do pedido)
7. Aguardar N-EVENT-REPORT dentro do timeout:
   - Event Type ID = 1: todos os items foram commitados com sucesso
   - Event Type ID = 2: alguns items falharam
8. Liberar associação
9. Retornar resultado estruturado

**Retorno:**
- `success: bool` - Se o commitment foi recebido
- `message: str` - Descrição do resultado
- `transaction_uid: str` - UID da transação
- `committed: List[Dict]` - Instâncias confirmadas com sucesso
- `failed: List[Dict]` - Instâncias que falharam (incluindo razão se disponível)

#### 2.2.5 Implementar método auxiliar `_parse_commitment_response`
Extrair dados do dataset do N-EVENT-REPORT de forma limpa:
- Iterar sobre ReferencedSOPSequence
- Iterar sobre FailedSOPSequence
- Converter para dicionários serializáveis

### 2.3 Modificações em `server.py`

#### 2.3.1 Criar ferramenta MCP `request_storage_commitment`

**Parâmetros da ferramenta:**
- `sop_instances: List[Dict[str, str]]` - Lista de instâncias para confirmar
- `timeout: int = 30` - Timeout opcional

**Documentação:**
- Explicar que é usado para confirmar armazenamento
- Documentar o formato esperado de sop_instances
- Explicar os possíveis resultados (success, partial, timeout)

**Implementação:**
- Obter cliente do contexto
- Chamar `client.request_storage_commitment()`
- Retornar resultado formatado

### 2.4 Tratamento de Erros

#### 2.4.1 Cenários a tratar
- SCP não suporta Storage Commitment (contexto rejeitado)
- N-ACTION falha (vários códigos de status)
- Timeout aguardando N-EVENT-REPORT
- Associação perdida durante operação
- Instâncias referenciadas não encontradas no SCP

#### 2.4.2 Mensagens de erro
Criar mensagens claras e acionáveis para cada cenário.

### 2.5 Testes

#### 2.5.1 Teste unitário do request builder
- Verificar estrutura correta do Dataset N-ACTION
- Verificar geração de TransactionUID

#### 2.5.2 Teste unitário do response parser
- Mock de N-EVENT-REPORT com sucesso total
- Mock de N-EVENT-REPORT com falhas parciais
- Mock de timeout

#### 2.5.3 Teste de integração
- Requer SCP que suporte Storage Commitment (Orthanc com plugin, DCM4CHEE, etc.)

---

## Parte 3: Integração e Documentação

### 3.1 Atualizar README.md
- Documentar novas funcionalidades
- Exemplos de uso via MCP
- Configuração do async_operations_window

### 3.2 Atualizar Prompt Guide
No `dicom_query_guide()` em server.py:
- Adicionar seção sobre Storage Commitment
- Explicar quando usar e limitações

### 3.3 Configuração
Atualizar exemplo de configuração YAML/JSON com novas opções.

---

## Ordem de Implementação Recomendada

1. **Async Operations** (mais simples, menos dependências)
   - 1.2.1 → 1.2.2 → 1.2.3 → 1.2.4 → 1.3 → 1.4

2. **Storage Commitment** (mais complexo)
   - 2.2.1 → 2.2.2 → 2.2.3 → 2.2.4 → 2.2.5 → 2.3 → 2.4 → 2.5

3. **Documentação**
   - 3.1 → 3.2 → 3.3

---

## Limitações Conhecidas

### Storage Commitment
- **Resposta na mesma associação**: Esta implementação assume que o SCP responde com N-EVENT-REPORT na mesma associação. Alguns PACS (especialmente mais antigos) podem enviar a resposta em uma nova associação reversa, o que requer implementar um SCP listener - fora do escopo inicial.

### Async Operations
- **Suporte variável**: Nem todos os PACS suportam async operations. O código deve gracefully fallback para operação síncrona se a negociação falhar.
- **Thread safety**: As operações paralelas devem ser thread-safe. Atenção especial ao compartilhamento de estado.

---

## Referências

- DICOM PS3.4 - Storage Commitment Push Model
- DICOM PS3.7 - Asynchronous Operations Window Negotiation
- pynetdicom docs: https://pydicom.github.io/pynetdicom/stable/
