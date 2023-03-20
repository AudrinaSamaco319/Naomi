const jokeEl = document.getElementById('joke')
const jokeBtn = document.getElementById('jokeBtn')

generateJoke()

jokeBtn.addEventListener('click', generateJoke)

async function generatejoke(){
    const response = await fetch('http://icanhazdadjoke.com', {
        headers: {Accept: 'application/json'}
    })

    const data = await response.json()
    jokeEl.innerHTML = data.joke
}