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

        function iniciarStream() {
            let index = document.getElementById("cameraSelect").value;
            let stream = document.getElementById("videoStream")
            let rota = stream.parentNode.id

            stream.src = `/video_${rota}/${index}`;

        }
