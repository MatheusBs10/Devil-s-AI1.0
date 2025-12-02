Projeto Antítese (The Devil’s AI): Imunologia Cognitiva com Análise Argumentativa em Tempo Real
1. Título do Projeto e Integrantes
Título Oficial: Projeto Antítese: Uma Abordagem de Imunologia Cognitiva Ativa via Debates Artificiais e Visualização de Dados em Tempo Real. Nome Curto/Comercial: The Devil’s AI
Integrantes do Grupo:
Matheus Beserra
Gabriel Sena
Diogo Ramon
2. Justificativa, Motivação e Diagnóstico
Diagnóstico do Problema e Desafios
Vivemos na era da "Pós-Verdade", onde a desinformação se espalha mais rápido que os fatos. O modelo tradicional de ensino ainda foca majoritariamente na transferência passiva de conhecimento ("o professor fala, o aluno aceita"). Com a ascensão das IAs generativas (como o ChatGPT), surgiu um novo desafio: a confiança cega. Os alunos tendem a aceitar as respostas da máquina como verdades absolutas, atrofiando sua capacidade de verificação e pensamento crítico.
O desafio central não é apenas ensinar o aluno a debater, mas tornar visível o invisível: mostrar ao aluno, enquanto ele fala, onde sua lógica está falhando ou onde ele está sendo enganado, permitindo uma correção de rota imediata.
A Solução e o Diferencial Inovador
A maioria das IAs educacionais tenta dar a resposta certa. O Projeto Antítese propõe o oposto: um sistema treinado para debater com o aluno defendendo teses sutilmente erradas, enviesadas ou falaciosas (ex: defender terraplanismo com física complexa).
O grande diferencial deste projeto, contudo, reside na sua Interface de Feedback Visual Contínuo. Diferente de um chat comum, a aplicação exibirá gráficos dinâmicos ao longo do debate. O sistema não apenas troca mensagens; ele monitora a "saúde lógica" da discussão, exibindo pontuação, identificando pontos fracos e alertando sobre instabilidade emocional ou argumentativa em tempo real.
Benefícios Esperados
Para o Aluno (Imunologia Cognitiva): O aluno deixa de ser um receptáculo passivo e torna-se um "investigador". O dashboard visual atua como um mecanismo de biofeedback lógico, ajudando na autorregulação. Ele vê sua pontuação cair se usar argumentos fracos e subir se identificar uma falácia da IA, gamificando o rigor intelectual.
Para o Professor: Oferece uma ferramenta escalável. O professor recebe relatórios detalhados sobre quais falácias seus alunos têm mais dificuldade em detectar (ex: a turma é boa em dados, mas cai em apelos emocionais), permitindo intervenções cirúrgicas.
3. Objetivos Geral e Específicos
Objetivo Geral
Desenvolver e validar um protótipo de Sistema de Tutoria Inteligente (STI) focado no "Aprendizado por Refutação", integrado a um painel analítico em tempo real que mensura e exibe a performance argumentativa do aluno enquanto ele tenta vencer uma IA propositalmente falaciosa.
Objetivos Específicos
Desenvolver o Motor de Debate (The Devil's AI): Criar "personas" de IA via Prompt Engineering treinadas para utilizar falácias lógicas específicas (ex: Ad Hominem, Espantalho, Falsa Causalidade, Declive Escorregadio) dentro de temas curriculares.
Implementar o Sistema de Análise Visual em Tempo Real (O Diferencial): Construir uma interface gráfica que exiba:
Um "Termômetro do Debate" (quem está ganhando a discussão momento a momento).
Indicadores de pontos fracos na argumentação do aluno instantaneamente.
Marcação visual de falácias detectadas ou não detectadas.
Criar o Módulo "Juiz": Implementar uma segunda instância de IA que atua como árbitro silencioso, analisando o texto do debate para alimentar os gráficos e a pontuação sem interromper o fluxo da conversa.
Mensurar a Imunidade Cognitiva: Validar se o feedback visual ajuda o aluno a identificar Fake News e falácias com mais rapidez e precisão do que um debate apenas em texto.
4. Metodologia
A solução será desenvolvida seguindo princípios de Engenharia de Prompt Avançada e Design de Interfaces de Dados (Data Visualization).
Arquitetura Técnica
O sistema operará com dois agentes de LLM (Large Language Models) simultâneos, utilizando APIs robustas (como OpenAI GPT-4 ou Llama 3 via Groq para baixa latência):
Agente Oponente (A IA Mentirosa): Instruída via System Prompt para agir como um sofista persuasivo. Exemplo de comando: "Você é um debatedor enviesado. Defenda que a Revolução Industrial foi prejudicial usando dados fora de contexto. Não ceda até que o aluno aponte especificamente sua falácia lógica."
Agente Juiz (O Analista de Dados): Este agente não interage com o aluno. Ele lê o histórico do chat em tempo real e extrai metadados para o Frontend: "O aluno identificou a falácia? A resposta do aluno foi baseada em fatos ou opinião? Atribua uma nota de 0 a 100 para este turno."
Interface do Usuário (O Core da Experiência)
A interface será dividida em duas áreas principais:
Área de Chat: Onde ocorre o diálogo textual.
Dashboard de Combate (HUD): A inovação do projeto. Uma barra lateral ou superior dinâmica contendo:
Gráfico de Oscilação de Poder: Uma linha do tempo que sobe ou desce conforme o aluno ganha ou perde terreno no argumento.
Radar de Falácias: Ícones que acendem quando a IA tenta um truque (para níveis fáceis) ou quando o aluno comete um erro lógico (feedback corretivo).
Indicador de "Sangramento": Alerta visual quando o aluno está focando em um ponto irrelevante enquanto a IA domina o tópico central.
Etapas de Desenvolvimento
Definição das Personas: Criação dos prompts para os temas (História, Física, Biologia).
Prototipagem do Frontend: Desenvolvimento da interface gráfica focada na visualização dos dados do debate.
Integração do Juiz: Conectar a saída analítica do LLM aos componentes gráficos da tela (React/WebSockets).
Teste Piloto: Aplicação com pequeno grupo para calibrar a sensibilidade dos gráficos (para não frustrar nem facilitar demais).
5. Resultados Esperados
Ao final da Unidade 3, espera-se entregar:
Protótipo Funcional: Um chatbot operacional capaz de sustentar debates sobre pelo menos 3 temas polêmicos (ex: Terra Plana, Eficácia de Vacinas, Interpretações Históricas), defendendo o lado incorreto.
Interface com Análise em Tempo Real: O sistema deve ser capaz de plotar gráficos de desempenho enquanto o texto é gerado, sem latência perceptível que atrapalhe a imersão.
Relatório de "Imunidade": Ao final do debate, o sistema gerará um dossiê visual (Dashboard Pós-Jogo) mostrando a evolução do aluno, onde ele hesitou e quais tipos de mentiras ele deixou passar.
Inovação em AIED: A demonstração prática de um novo paradigma onde a "alucinação" da IA é uma feature, não um bug, e onde a visualização de dados serve como ferramenta de autorregulação emocional e lógica para o estudante.


