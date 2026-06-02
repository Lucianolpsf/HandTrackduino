function clearMediaSrcs() {
    const content = document.getElementById('content');
    if (!content) return;
    // Limpa src de todos os elementos de mídia dentro do container
    ['img'].forEach(tag => {
        content.querySelectorAll(tag).forEach(el => {
            el.src = '';
            el.remove();
        });
    });
}

function loadContent(id) {
    clearMediaSrcs(); // Limpa mídias antes de carregar novo conteúdo
    if (id === 1) {
        fetch('/arduino')
        .then(response => response.text())
        .then(html => {
            document.getElementById('content').innerHTML = html;
            console.log(`${html}`);
        });
    }
    else if (id === 2) {
        fetch('/lousa')
        .then(response => response.text())
        .then(html => {
            document.getElementById('content').innerHTML = html;
            console.log(`${html}`);
        });
    }
    else if (id === 3) {
        fetch('/jokenpo')
        .then(response => response.text())
        .then(html => {
            document.getElementById('content').innerHTML = html;
            console.log(`${html}`);
        });
    }
    else {
        fetch(`/conteudo/${id}`)
        .then(response => response.json())
        .then(data => {
            document.getElementById('content').innerHTML = `<p>${data.conteudo}</p>`;
        });
    }
}