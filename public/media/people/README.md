# Fotos dos participantes

Para exibir a **foto** de uma pessoa no lugar das iniciais do avatar:

1. Coloque o arquivo aqui como `{{id}}.jpg` (ex.: `daniel-vorcaro.jpg`,
   `flavio-bolsonaro.jpg`).
2. No `data/participants.json`, preencha o campo `"photo"` do participante com o
   nome do arquivo (ex.: `"photo": "flavio-bolsonaro.jpg"`).

Sem foto (`"photo": null`) o avatar mostra as iniciais — nunca é usada foto
inventada, gerada ou sem direito de publicação. Se a imagem falhar ao carregar,
as iniciais voltam automaticamente.
