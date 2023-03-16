button = document.querySelector('.btn')
search = document.querySelector('.search')


button.addEventListener('click',() => {
    console.log("HELLO")
    search.classList.toggle('active')
})