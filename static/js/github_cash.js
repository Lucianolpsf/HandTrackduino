function renderCards(cards) {
    let html = '';
    for (const card of cards) {
        html += `
        <div class="card" >
            <div class="card-header">
                <img src="${card.avatar_url}" alt="Avatar">
                <div>
                    <img src="${card.qr_code}" alt="QR Code">
                </div>
            </div>
            <div><strong>${card.name}</strong></div>
        </div>
        `;
    }
    document.getElementById('cards-container').innerHTML = html;
}

document.addEventListener('DOMContentLoaded', function() {
    const cached = localStorage.getItem('github_cards');
    if (cached) {
        renderCards(JSON.parse(cached));
    } else {
        fetch('/cards_json')
            .then(resp => resp.json())
            .then(cards => {
                localStorage.setItem('github_cards', JSON.stringify(cards));
                renderCards(cards);
            });
    }
});