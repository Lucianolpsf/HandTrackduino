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
document.getElementById("cameraSelect").addEventListener("change", setCameraIndex);

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
