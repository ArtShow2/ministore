// main.js

// confirmação de exclusão — já está nos templates via onsubmit
// este arquivo é reservado para funcionalidades futuras

// destacar item do menu ativo
document.addEventListener('DOMContentLoaded', function() {
    const links = document.querySelectorAll('nav a');
    links.forEach(link => {
        if (link.href === window.location.href) {
            link.classList.add('ativo');
        }
    });
});