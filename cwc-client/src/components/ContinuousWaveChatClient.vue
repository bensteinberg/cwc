<style>
</style>

<script setup lang="ts">
// imports
import { ref, computed, watch } from 'vue'

import { useWebSocket } from '@vueuse/core'

import _morse from '../morse-code.json'

// interfaces
interface MorseMapping {
    [key: string]: string
}

interface Morse {
    character: string, morse: string
}

export interface MorseList extends Array<Morse> { }

// reactive "constants"
const morse: MorseMapping = _morse

const message = ref("")
const frequency = ref(700)
const wpm = ref(25)
const decode = ref(true)
const play = ref(false)
const playing = ref(false)
const messageQueue = ref<string[]>([])

const audioContextInitialized = ref(false)
const volume = ref(0.0)

const channels = [...Array(16).keys()]
const channel = ref(0)

const paris = morseToDits(textToMorse("paris "))

// is there something like doctest?
// console.assert(paris === 50, "Paris is not 50!")
// console.assert(morseToDits(textToMorse("codex ")) === 60, "Codex is not 60!")
// console.assert(morseToDits(textToMorse("paris ".repeat(5))) === 250, "5x Paris is not 250!")
// console.assert(morseToDits(textToMorse("paris  ".repeat(5))) === 285, "5x Paris with extra spaces is not 285!")



const ditLength = computed(() => {
    return (60 * 1000) / (wpm.value * paris)
})

const dashLength = computed(() => {
    return 3 * ditLength.value
})

// set up websocket
const { ws } = useWebSocket(import.meta.env.VITE_WEBSOCKET, {
    autoReconnect: true,
    onConnected:(webSocket)=>{
       webSocket.addEventListener('message', function (event) {
            let transmission = JSON.parse(event.data)
            if (transmission.channel === channel.value) {
                messageQueue.value.push(transmission.message)
                if (!(playing.value)) {
                    playing.value = true
                    playNext()
                }
            }
        })
    },
})

function playNext() {
    try {
        let transmission = messageQueue.value.shift()
        if (transmission) {
            let msg = textToMorse(transmission)
            playing.value = true
            setTimeout(function() {playing.value = false ; playNext()}, 7 * dashLength.value + morseToDits(msg) * ditLength.value)
            playMorse(msg)
        }
    } catch(error) {
        console.log(error)
    }
}

// Morse functions
function textToMorse(text: string) {
    return text.toLowerCase().split('').filter(c => c in morse || c === " ").map(
        function(c) {
            if (c === " ") {
                return {character: " ", morse: "/" }
            } else {
                return {character: c, morse: morse[c]}
            }
        }
    )
}

function morseToDits(characters: MorseList) {
    let characterCount = characters.length
    let nonSpaceCharacters = characters.filter((c) => c.morse !== "/")
    let intraCharacterSpaces = nonSpaceCharacters.map((c) => c.morse.length - 1).reduce((partialSum, a) => partialSum + a, 0)
    let spaces = characterCount - nonSpaceCharacters.length
    // there must be a better way to do this
    let groupedWhitespace = 0
    let lastCharacter = null
    for (let i = 0 ; i < characters.length ; i++) {
        if (characters[i].morse === "/" && lastCharacter !== "/") {
            groupedWhitespace++
        }
        lastCharacter = characters[i].morse
    }
    let interCharacterSpaces = nonSpaceCharacters.length - groupedWhitespace
    let allDits = nonSpaceCharacters.map((c) => c.morse.split(".").length - 1).reduce((partialSum, a) => partialSum + a, 0)
    let allDashes = nonSpaceCharacters.map((c) => c.morse.split("-").length - 1).reduce((partialSum, a) => partialSum + a, 0)
    return allDits + (3 * allDashes) + (7 * spaces) + intraCharacterSpaces + (3 * interCharacterSpaces)
}

// action on enter in text input
function sendMessage() {
    const msg = message.value
    if (msg) {
        ws.value!.send(JSON.stringify(
            {
                "channel": channel.value,
                "message": msg
            }
        ))
    }
    message.value = ""
    return false
}

// audio context setup
let note_context
let note_node: OscillatorNode
let gain_node: GainNode

function initializeAudioContext() {
    note_context = new AudioContext()
    note_node = note_context.createOscillator()
    gain_node = note_context.createGain()
    note_node.frequency.value = frequency.value
    gain_node.gain.value = 0
    note_node.connect(gain_node)
    gain_node.connect(note_context.destination)
    note_node.start()
    audioContextInitialized.value = true
}

function changeFrequency(freq: number) {
    note_node.frequency.value = freq
}

watch(frequency, (newFrequency) => {
    changeFrequency(newFrequency)
})

watch(volume, (newVolume) => {
    if (newVolume !== 0.0) {  
        if (!audioContextInitialized.value) {
            initializeAudioContext()
        }
    }
})

watch(play, (newPlay) => {
    if (newPlay) {
        if (!audioContextInitialized.value) {
            initializeAudioContext()
        }
    }
})

// functions for playing dots and dashes and combinations
function startNotePlaying() {
    // Pass a start time of 0 so it starts ramping up immediately.
    gain_node.gain.setTargetAtTime(volume.value, 0, 0.01)
}

function stopNotePlaying() {
    // Pass a start time of 0 so it starts ramping down immediately.
    gain_node.gain.setTargetAtTime(0, 0, 0.01)
}

function sleep(ms: number) {
    return new Promise(resolve => setTimeout(resolve, ms))
}

async function playDash() {
    startNotePlaying()
    await sleep(dashLength.value)
    stopNotePlaying()
}

async function playDot() {
    startNotePlaying()
    await sleep(ditLength.value)
    stopNotePlaying()
}

async function playLetter(letter: Morse) {
    if (!play.value) {
        return
    }
    if (!audioContextInitialized.value) {
        initializeAudioContext()
    }
    const div = document.getElementById("messages")
    let oldText = div!.firstChild!.textContent
    for (let i = 0; i < letter["morse"].length; i++) {
        if (letter["morse"][i] == '-') {
            await playDash()
        } else if (letter["morse"][i] == '.') {
            await playDot()
        }
        await sleep(ditLength.value)
    }
    div!.firstChild!.textContent = oldText + letter["character"]
}

async function playMorse(word: MorseList) {
    // erase previous sentence
    const div = document.getElementById("messages")
    div!.firstChild!.textContent = ""
    for (let i = 0; i < word.length; i++) {
        await playLetter(word[i])
        await sleep(dashLength.value)
    }

}

</script>

<template>
  <h1>cwc</h1>
  <div class="grid">
    <div>
      <input type="text" name="message" minlength="1" v-model="message" @keyup.enter="sendMessage"/>
    </div>
    <div id="messages">
      <p v-if="decode" class="message"></p>
    </div>
  </div>
  <div id="settings">
    <label>
      Channel
      <select name="channel" v-model="channel">
        <option v-for="c in channels" :value="c" :key="c">
          {{ c }}
        </option>
      </select>
    </label>
    <label>
      WPM: {{ wpm }}
      <input type="range" v-model="wpm" name="WPM">
    </label>
    <label>
      Audio frequency: {{ frequency }}
      <input type="range" v-model="frequency" name="frequency" min="0" max="1500">
    </label>
    <label>
      Volume: {{ volume * 500 }}
      <input type="range" v-model="volume" name="volume" min="0.0" max="0.2" step="0.01">
    </label>
    <label>
      Play
      <input name="play" type="checkbox" role="switch" v-model="play"/>
    </label>
    <label>
      “decode”
      <input name="decode" type="checkbox" role="switch" v-model="decode"/>
    </label>
  </div>
</template>
