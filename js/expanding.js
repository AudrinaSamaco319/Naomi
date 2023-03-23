const panels = document.querySelectorAll('.panel')


panels.forEach(panel => {
    panel.addEventListener('click', () => {
        closePanel()
        panel.classList.add('active')
    })
})


function closePanel() {
    panels.forEach(panel => {
        panel.classList.remove('active')
    })
}