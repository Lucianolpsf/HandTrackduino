// Carrega as câmeras disponíveis
fetch("/cameras")
    .then(response => response.json())
    .then(cameras => {
        let select = document.getElementById("cameraSelect");
        cameras.forEach(index => {
            let option = document.createElement("option");
            option.value = index;
            option.text = "Câmera " + index;
            select.appendChild(option);
        });
    });

function setCameraIndex() {
    let index = document.getElementById("cameraSelect").value;
    fetch("/set_camera", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ camera_index: index })
    }).then(response => response.json())
      .then(data => {
          console.log("Câmera definida:", data.camera_index);
      });
}

// Chame setCameraIndex() sempre que o usuário selecionar uma câmera
document.getElementById("cameraSelect").addEventListener("click", setCameraIndex);

function iniciarStream() {
    let stream = document.getElementById("videoStream");
    let rota = stream.parentNode.id;
    // Agora não precisa mais passar o índice na URL
    stream.src = `/video_${rota}`;
}

// camera.js
window.addEventListener("beforeunload", function (e) {
    navigator.sendBeacon("/release_camera");
});

window.onload = function() {
    fetch('/arduino_ports')
        .then(response => response.json())
        .then(ports => {
            const select = document.getElementById('arduinoPortSelect');
            ports.forEach(port => {
                const option = document.createElement('option');
                option.value = port;
                option.text = port;
                select.appendChild(option);
            });
            // Adiciona o evento change após popular as opções
            select.addEventListener('click', setArduinoPort);
        });
};

function setArduinoPort() {
    const port = document.getElementById('arduinoPortSelect').value;
    fetch('/set_arduino_port', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({port: port})
    }).then(resp => resp.json())
      .then(data => console.log(data.status));
}