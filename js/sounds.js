const sounds = {'applause', 'boo' , 'gasp , 'tada' , 'victory' , 'wrong'

sounds.forEach(sound => {
    const btn = document.createElement('button')
    btn.classList.add('btn')
    btn.innerText = sound

    btn.addEventListener('click', () =>{
        document.getElementById(sound).play()
    })


    document.getElementById('button').appendChild(btn)
})

Function stopSongs() {
    sounds.forEach(sound => {
        const song = document.getElementById(sound)
        song.pause()
        song.currentTime = 0
    })
}