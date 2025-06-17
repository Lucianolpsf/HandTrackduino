// Aguarda o carregamento completo do DOM antes de executar o script
document.addEventListener('DOMContentLoaded', () => {
    // Obtenção de referências para os elementos HTML do jogo
    const playerScoreSpan = document.getElementById('player-score');
    const aiScoreSpan = document.getElementById('ai-score');
    const tiesSpan = document.getElementById('ties');
    const roundsPlayedSpan = document.getElementById('rounds-played');
    const resetScoreboardButton = document.getElementById('reset-scoreboard');
    const robotChoiceIcon = document.getElementById('robot-choice-icon');
    const aiCountdownMessage = document.getElementById('ai-countdown-message');
    const aiResultMessage = document.getElementById('ai-result-message');
    const roundResultMain = document.getElementById('round-result-main');
    const handDetectedStatus = document.getElementById('hand-detected-status');
    const detectedGestureFeedback = document.getElementById('detected-gesture-feedback');
    const jokenpoJsonDisplay = document.getElementById('jokenpo-json-display');
    const videoStream = document.getElementById('videoStream');

    // Variáveis para armazenar o estado do placar
    let playerScore = 0;
    let aiScore = 0;
    let ties = 0;
    let roundsPlayed = 0;

    // Opções possíveis do jogo Jokenpo
    const choices = ['rock', 'paper', 'scissors'];

    /**
     * Atualiza os valores exibidos no placar do jogo.
     */
    const updateScoreboard = () => {
        playerScoreSpan.textContent = playerScore;
        aiScoreSpan.textContent = aiScore;
        tiesSpan.textContent = ties;
        roundsPlayedSpan.textContent = roundsPlayed;
    };

    /**
     * Simula uma rodada do jogo Jokenpo, incluindo a escolha da IA,
     * a determinação do vencedor e a atualização do placar.
     */
    const playRound = () => {
        roundsPlayed++;
        updateScoreboard();

        // Simula a escolha do jogador (ex: a partir da detecção da câmera)
        // Para demonstração, uma escolha aleatória é feita.
        const playerChoice = choices[Math.floor(Math.random() * choices.length)];
        handDetectedStatus.textContent = 'Sim'; // Simula mão detectada
        detectedGestureFeedback.textContent = playerChoice.charAt(0).toUpperCase() + playerChoice.slice(1);

        // Simula a escolha da IA
        const aiChoice = choices[Math.floor(Math.random() * choices.length)];

        // Atualiza a exibição da IA
        aiCountdownMessage.textContent = 'IA escolhendo...';
        robotChoiceIcon.innerHTML = '<i class="fas fa-question"></i>'; // Reinicia o ícone temporariamente

        // Simula o tempo de "pensamento" da IA antes de revelar a jogada
        setTimeout(() => {
            aiCountdownMessage.textContent = 'Aguarde...'; // Mantém um texto padrão
            aiResultMessage.textContent = `A IA escolheu: ${aiChoice.charAt(0).toUpperCase() + aiChoice.slice(1)}`;

            // Atualiza o ícone da IA com base na escolha
            if (aiChoice === 'rock') {
                robotChoiceIcon.innerHTML = '<i class="fas fa-hand-rock"></i>';
            } else if (aiChoice === 'paper') {
                robotChoiceIcon.innerHTML = '<i class="fas fa-hand-paper"></i>';
            } else if (aiChoice === 'scissors') {
                robotChoiceIcon.innerHTML = '<i class="fas fa-hand-scissors"></i>';
            }

            // Determina o resultado da rodada
            let result = '';
            if (playerChoice === aiChoice) {
                result = 'Empate!';
                ties++;
            } else if (
                (playerChoice === 'rock' && aiChoice === 'scissors') ||
                (playerChoice === 'paper' && aiChoice === 'rock') ||
                (playerChoice === 'scissors' && aiChoice === 'paper')
            ) {
                result = 'Você Ganhou!';
                playerScore++;
            } else {
                result = 'A IA Ganhou!';
                aiScore++;
            }

            roundResultMain.textContent = result; // Exibe o resultado principal da rodada
            updateScoreboard(); // Atualiza o placar

            // Atualiza a exibição JSON de depuração com o estado atual do jogo
            const jokenpoState = {
                playerScore: playerScore,
                aiScore: aiScore,
                ties: ties,
                roundsPlayed: roundsPlayed,
                lastPlayerChoice: playerChoice,
                lastAIChoice: aiChoice,
                lastRoundResult: result
            };
            jokenpoJsonDisplay.textContent = JSON.stringify(jokenpoState, null, 2);

            // Reinicia as mensagens e ícones após um curto atraso para a próxima rodada
            setTimeout(() => {
                roundResultMain.textContent = 'Aguardando...';
                aiResultMessage.textContent = 'Aguardando jogada da IA...'; // Mantém um texto padrão
                aiCountdownMessage.textContent = 'Aguarde...'; // Mantém um texto padrão
                robotChoiceIcon.innerHTML = '<i class="fas fa-question"></i>';
                handDetectedStatus.textContent = 'Não';
                detectedGestureFeedback.textContent = 'Nenhum';
            }, 2000);

        }, 1000); // Tempo de simulação da IA (1 segundo)
    };

    // Adiciona event listeners aos botões


    resetScoreboardButton.addEventListener('click', () => {
        // Reinicia todas as variáveis do placar
        playerScore = 0;
        aiScore = 0;
        ties = 0;
        roundsPlayed = 0;
        updateScoreboard(); // Atualiza o placar exibido

        // Reinicia todas as mensagens e estados visuais para seus valores padrão
        roundResultMain.textContent = 'Aguardando...';
        aiResultMessage.textContent = 'Aguardando jogada da IA...'; // Define um texto padrão
        aiCountdownMessage.textContent = 'Aguarde...'; // Define um texto padrão
        robotChoiceIcon.innerHTML = '<i class="fas fa-question"></i>';
        handDetectedStatus.textContent = 'Não';
        detectedGestureFeedback.textContent = 'Nenhum';
        jokenpoJsonDisplay.textContent = '{}'; // Limpa o JSON de depuração
    });

});
