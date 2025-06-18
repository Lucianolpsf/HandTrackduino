document.addEventListener('DOMContentLoaded', () => {
    // --- Elementos HTML da Câmera e Jokenpo ---
    const cameraFeed = document.getElementById('camera-feed'); 
    const cameraStatus = document.getElementById('camera-status');
    // REMOVIDOS: startProcessingButton, stopProcessingButton (porque os botões foram removidos do HTML)

    // --- Ícones de Gesto ---
    const playerLiveGestureIcon = document.getElementById('player-live-gesture-icon');
    const robotChoiceIcon = document.getElementById('robot-choice-icon');

    // --- Jokenpo HTML Elements (placar) ---
    const playerScoreSpan = document.getElementById('player-score');
    const aiScoreSpan = document.getElementById('ai-score');
    const tiesSpan = document.getElementById('ties'); 
    const roundsPlayedSpan = document.getElementById('rounds-played');
    
    // --- Área de Mensagens do Jogo ---
    const roundResultMain = document.getElementById('round-result-main'); 
    // REMOVIDOS: countdownMessageElement (não existe em jokenpo_game_state do app.py)
    const aiCountdownMessage = document.getElementById('ai-countdown-message'); // Apenas um placeholder, não preenchido
    const aiResultMessage = document.getElementById('ai-result-message'); 

    // --- Botões de Controle e Informações de Depuração ---
    const playRoundButton = document.getElementById('play-round-button');
    const finishRoundButton = document.getElementById('finish-round-button'); 
    const resetScoreboardButton = document.getElementById('reset-scoreboard');
    const handDetectedStatus = document.getElementById('hand-detected-status');
    const detectedGestureFeedback = document.getElementById('detected-gesture-feedback');
    const jokenpoJsonDisplay = document.getElementById('jokenpo-json-display');

    // --- Mapeamento de Jogadas para Ícones Font Awesome ---
    const jokenpoIcons = {
        "Pedra": "fas fa-hand-rock",
        "Papel": "fas fa-hand-paper",
        "Tesoura": "fas fa-hand-scissors",
        "Nenhum": "fas fa-question", 
        "Indefinido": "fas fa-question" 
    };

    // --- Função para atualizar o estado do Jokenpo e a UI ---
    async function updateJokenpoGameDisplay() {
        try {
            const response = await fetch('/jokenpo_game_status');
            if (!response.ok) {
                throw new Error(`Erro HTTP: ${response.status}`);
            }
            const data = await response.json();
            
            jokenpoJsonDisplay.textContent = JSON.stringify(data, null, 2);

            // Atualiza o status da câmera
            if (data.camera_is_active) {
                cameraStatus.textContent = 'Câmera do Backend Ativa';
                cameraStatus.style.backgroundColor = 'rgba(46, 204, 113, 0.8)'; 
            } else {
                cameraStatus.textContent = 'Câmera do Backend Inativa/Erro';
                cameraStatus.style.backgroundColor = 'rgba(231, 76, 60, 0.8)'; 
            }

            // Atualiza os elementos do placar
            playerScoreSpan.textContent = data.player_score;
            aiScoreSpan.textContent = data.ai_score;
            tiesSpan.textContent = data.ties || 0; 
            roundsPlayedSpan.textContent = data.rounds_played;

            // Atualiza o ícone do gesto ao vivo do jogador (usa 'current_gesture' do backend)
            playerLiveGestureIcon.innerHTML = `<i class="${jokenpoIcons[data.current_gesture]}"></i>`;
            
            // Atualiza o ícone da escolha da IA
            robotChoiceIcon.innerHTML = `<i class="${jokenpoIcons[data.ai_choice]}"></i>`; 

            // Atualiza a mensagem de resultado da rodada
            roundResultMain.textContent = data.result; 
            roundResultMain.className = ''; // Reseta classes
            if (data.result === 'Ganhou') { 
                roundResultMain.classList.add('won');
            } else if (data.result === 'Perdeu') {
                roundResultMain.classList.add('lost');
            } else if (data.result === 'Empate') {
                roundResultMain.classList.add('draw');
            } else { // Caso "Aguardando Jogada"
                roundResultMain.classList.add('neutral');
            }

            // AI's game feedback (usando 'result')
            aiCountdownMessage.textContent = ""; // Backend não fornece contagem regressiva específica para IA aqui
            aiResultMessage.textContent = data.result; 
            aiResultMessage.className = 'result-ai'; // Reseta classes
            if (data.result === 'Ganhou') {
                aiResultMessage.classList.add('lost'); // Se jogador venceu, IA perdeu
            } else if (data.result === 'Perdeu') {
                aiResultMessage.classList.add('won'); // Se IA venceu, IA venceu
            } else if (data.result === 'Empate') {
                aiResultMessage.classList.add('draw'); 
            } else {
                 aiResultMessage.classList.add('neutral');
            }

            // Atualiza o status de detecção de mão (para depuração)
            if (data.hand_detected) {
                handDetectedStatus.textContent = 'Sim';
                handDetectedStatus.style.color = '#2ecc71';
            } else {
                handDetectedStatus.textContent = 'Não';
                handDetectedStatus.style.color = '#e74c3c';
            }

            // Atualiza o feedback do gesto detectado pelo backend (para depuração)
            detectedGestureFeedback.textContent = data.current_gesture;

            // --- Lógica de Habilitação/Desabilitação de Botões ---
            // O botão "Jogar Rodada" deve ser desabilitado se não houver mão detectada
            // ou se o resultado ainda não foi determinado ("Aguardando Jogada")
            if (!data.hand_detected || data.result !== "Aguardando Jogada") {
                 playRoundButton.disabled = true;
            } else {
                playRoundButton.disabled = false;
            }

            // O botão "Terminar Rodada" está sempre oculto (você pode remover do HTML se não for usar)
            finishRoundButton.style.display = 'none';
            
            // Re-habilitar o botão de jogar se o resultado for algo diferente de "Aguardando Jogada"
            // Isso permite clicar para iniciar uma nova rodada após o término de uma.
            if (data.result === "Ganhou" || data.result === "Perdeu" || data.result === "Empate") {
                playRoundButton.disabled = false; 
                playRoundButton.textContent = "Jogar Novamente"; 
                playRoundButton.classList.remove('success'); 
                playRoundButton.classList.add('info'); 
            } else {
                playRoundButton.textContent = "Jogar Rodada"; 
                playRoundButton.classList.remove('info');
                playRoundButton.classList.add('success');
            }

        } catch (error) {
            console.error('Erro ao obter status do Jokenpo:', error);
            roundResultMain.textContent = "Erro de Conexão com Backend.";
            roundResultMain.classList.add('lost');
            cameraStatus.textContent = 'Erro de Conexão com Backend';
            cameraStatus.style.backgroundColor = 'rgba(231, 76, 60, 0.8)';
            playRoundButton.disabled = true;
            finishRoundButton.disabled = true;
        }
    }

    // Intervalo de atualização do display do jogo
    setInterval(updateJokenpoGameDisplay, 100);

    // --- Controles de Jogo ---
    // startProcessingButton e stopProcessingButton REMOVIDOS do JS

    playRoundButton.addEventListener('click', async () => {
        try {
            // A rota play_jokenpo do backend não espera o player_choice no URL
            // Ela usa o 'current_gesture' já disponível no jokenpo_game_state no backend.
            const response = await fetch('/play_jokenpo'); // Chamada sem parâmetro no URL
            const data = await response.json();
            console.log('Resultado da jogada:', data);

            if (data.status === "error") {
                // Substituir alert por uma mensagem no frontend para melhor UX
                roundResultMain.textContent = data.message;
                roundResultMain.classList.add('lost'); // Indicar erro
            }
            updateJokenpoGameDisplay(); // Força atualização do display
        } catch (error) {
            console.error('Erro ao iniciar rodada:', error);
            roundResultMain.textContent = 'Não foi possível iniciar a rodada. Verifique a conexão com o servidor.';
            roundResultMain.classList.add('lost'); // Indicar erro
        }
    });

    // finishRoundButton.addEventListener (ainda com display:none no HTML)

    resetScoreboardButton.addEventListener('click', async () => {
        try {
            const response = await fetch('/reset_jokenpo');
            const data = await response.json();
            console.log('Placar Resetado:', data.message);
            updateJokenpoGameDisplay(); // Força atualização do display
        } catch (error) {
            console.error('Erro ao resetar placar:', error);
        }
    });

    // Chama a função de atualização do Jokenpo na inicialização da página
    updateJokenpoGameDisplay(); 
});
