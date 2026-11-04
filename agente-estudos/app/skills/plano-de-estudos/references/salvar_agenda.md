# Salvar a Agenda no Google Cloud Storage (GCSToolset)

O agente salva a agenda num arquivo CSV no Google Cloud Storage usando o **GCSToolset** do ADK ([adk.dev/integrations/gcs](https://adk.dev/integrations/gcs/)). Os arquivos são armazenados como objetos em um bucket GCS, e a pessoa pode baixar o arquivo gerado para importar no Google Agenda.

---

## Ferramentas disponíveis

| Ferramenta | Para que serve | Argumentos |
|---|---|---|
| `create_object` | Cria o objeto ou **sobrescreve** o objeto inteiro no bucket | `bucket_name` (texto), `object_name` (texto), `data` (texto) |
| `get_object_data` | Lê um objeto e devolve o seu conteúdo | `bucket_name` (texto), `object_name` (texto) |
| `list_objects` | Lista os objetos existentes no bucket | `bucket_name` (texto), `prefix` (opcional) |

Use o nome de bucket informado na instrução inicial do agente (ou na variável de ambiente `GCS_BUCKET_NAME`).

## Regras de objeto

* Use sempre o nome de objeto `plano-de-estudos.csv`.
* Use sempre o mesmo nome de objeto. No replanejamento, a versão nova substitui a anterior.

## Como gravar a agenda

1. Monte o CSV completo seguindo as regras de `assets/plano_template.md`.
2. Antes de chamar a ferramenta, confira o checklist:
   - [ ] A primeira linha é exatamente `Subject,Start Date,Start Time,End Date,End Time,Description`.
   - [ ] Há uma linha por sessão, sem linhas em branco, e nenhuma sessão cai em dia que a pessoa não informou.
   - [ ] Datas em `MM/DD/YYYY` e horários em `HH:MM AM/PM`.
   - [ ] Toda `Description` está entre aspas duplas.
   - [ ] O conteúdo **não** tem a cerca ```` ```csv ```` nem texto explicativo, só o CSV.
3. Chame `create_object` passando `bucket_name`, `object_name` igual a `plano-de-estudos.csv` e `data` igual ao CSV, terminando com uma quebra de linha.

Exemplo de chamada:

```json
{
  "bucket_name": "agente-estudos-planos",
  "object_name": "plano-de-estudos.csv",
  "data": "Subject,Start Date,Start Time,End Date,End Time,Description\n📚 Python: variáveis e entrada/saída,11/02/2026,08:00 PM,11/02/2026,09:00 PM,\"Revisão: — | Técnica: Aprender fazendo | Entregável: script de nome e idade\"\n"
}
```

## Como interpretar a resposta

| Resposta da ferramenta | O que fazer |
|---|---|
| `{"status": "SUCCESS", "results": "..."}` | Sucesso. Informe na seção 5 do template a localização `gs://<bucket>/plano-de-estudos.csv` e o número de sessões. |
| `{"status": "ERROR", "error_details": "..."}` | Ocorreu um erro ao gravar no GCS. Não insista. Diga em uma frase que não foi possível salvar o arquivo no bucket e mostre o CSV num bloco ```` ```csv ```` na seção 5. |

Nunca diga que salvou o arquivo sem ter recebido `"status": "SUCCESS"`.

## Replanejamento

1. Se precisar lembrar do plano atual, chame `get_object_data` com o `bucket_name` e `object_name` igual a `plano-de-estudos.csv`.
2. O conteúdo vem no campo `results`.
3. Se a resposta for de erro ou o objeto não for encontrado, monte o CSV a partir da tabela de sessões da conversa.
4. Monte o CSV novo **inteiro**, já com os ajustes, e grave com `create_object` no mesmo bucket e `object_name`. A versão anterior é substituída.
5. Na resposta, diga o que mudou e confirme que o arquivo foi atualizado.
