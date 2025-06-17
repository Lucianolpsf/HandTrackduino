function toggleArduino(checkbox) {
const estado = checkbox.checked ? 'on' : 'off';

fetch(`/arduino_automatico?estado=${estado}`, {
    method: 'GET'
}).then(response => {
    if (!response.ok) {
    alert("Erro ao comunicar com o servidor.");
    }
});
}