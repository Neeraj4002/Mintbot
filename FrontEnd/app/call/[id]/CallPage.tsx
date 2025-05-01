"use client"

declare global {
  interface Window {
    __RTC_CONFIGURATION__?: RTCConfiguration
  }
}

import { useEffect, useRef, useState } from "react"
import { useRouter } from "next/navigation"
import { Mic, PhoneOff, ArrowLeft } from "lucide-react"
import { Button } from "@/components/ui/button"
import { characters } from "@/data/characters"

export default function CallPage({ id }: { id: string }) {
  const [callTime, setCallTime] = useState(0)
  const [isCallActive, setIsCallActive] = useState(true)
  const router = useRouter()

  // Find selected character by id
  const character = characters.find((c) => c.id === id) || characters[0]

  // Refs for WebRTC and media
  const peerConnectionRef = useRef<RTCPeerConnection | null>(null)
  const webrtcIdRef = useRef<string>("")
  const localStreamRef = useRef<MediaStream | null>(null)
  // Guard to prevent double setup under React Strict Mode
  const webrtcSetupRef = useRef<boolean>(false)

  const formatTime = (s: number) =>
    `${String(Math.floor(s / 60)).padStart(2, "0")}:${String(s % 60).padStart(2, "0")}`

  // Call timer
  useEffect(() => {
    if (!isCallActive) return
    const interval = setInterval(() => setCallTime((t) => t + 1), 1000)
    return () => clearInterval(interval)
  }, [isCallActive])

  // Fetch STUN/TURN config
  async function getRTCConfigFromHTML(): Promise<RTCConfiguration> {
    const config: RTCConfiguration = {
      iceServers: [{ urls: "stun:stun.l.google.com:19302" }]
    }
    window.__RTC_CONFIGURATION__ = config
    return config
  }

  // Setup WebRTC with microphone capture and data channel
  async function setupWebRTC() {
    const webrtc_id = Math.random().toString(36).substring(2, 10)
    webrtcIdRef.current = webrtc_id

    const config = await getRTCConfigFromHTML()
    const pc = new RTCPeerConnection(config)
    peerConnectionRef.current = pc

    // Request mic access
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
      localStreamRef.current = stream
      stream.getTracks().forEach((track) => pc.addTrack(track, stream))
    } catch (err) {
      console.error("Error accessing the microphone:", err)
      alert("Failed to get microphone permission.")
      return
    }

    // Play remote audio
    pc.ontrack = (evt) => {
      const remoteAudio = new Audio()
      remoteAudio.srcObject = evt.streams[0]
      remoteAudio.onloadedmetadata = () => remoteAudio.play().catch(console.error)
    }

    // Data channel for input_hook
    const dataChannel = pc.createDataChannel("text")
    let dataChannelHandled = false
    dataChannel.onmessage = (e) => {
      if (dataChannelHandled) return
      dataChannelHandled = true
      try {
        const msg = JSON.parse(e.data)
        if (msg.type === "send_input") {
          // Include character.id so backend uses correct prompt
          fetch("http://localhost:8000/input_hook", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
              character: character.id,
              webrtc_id,
              api_key: "AIzaSyB-CXqCqmdcxv-WiaoNKa5mQpHw0n_A_aE",
              voice_name: character.voice,
            })
          }).catch(console.error)
        }
      } catch (err) {
        console.error("Error parsing dataChannel message:", err)
      }
    }

    // ICE candidate trickle
    pc.onicecandidate = (e) => {
      if (e.candidate) {
        fetch("http://localhost:8000/webrtc/offer", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            character: character.id,
            type: "ice-candidate",
            webrtc_id,
            candidate: e.candidate.toJSON()
          })
        }).catch(console.error)
      }
    }

    // SDP offer/answer
    const offer = await pc.createOffer()
    await pc.setLocalDescription(offer)
    await new Promise((resolve) => {
      if (pc.iceGatheringState === "complete") resolve(null)
      else pc.onicegatheringstatechange = () => {
        if (pc.iceGatheringState === "complete") resolve(null)
      }
    })
    const answerRes = await fetch("http://localhost:8000/webrtc/offer", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        character: character.id,
        webrtc_id,
        type: offer.type,
        sdp: offer.sdp
      })
    })
    const answer = await answerRes.json()
    if (!answer?.type || !answer?.sdp) {
      console.error("Invalid SDP answer from backend:", answer)
      return
    }
    await pc.setRemoteDescription(answer)
    console.log("WebRTC connected for character:", character.id)
  }

  // End call: cleanup and navigate
  const endCall = () => {
    setIsCallActive(false)
    if (peerConnectionRef.current) {
      peerConnectionRef.current.close()
      peerConnectionRef.current = null
    }
    if (localStreamRef.current) {
      localStreamRef.current.getTracks().forEach((track) => track.stop())
      localStreamRef.current = null
    }
    router.push(`/chat/${id}`)
  }

  // Guarded effect: only setup once under Strict Mode
  useEffect(() => {
    if (!isCallActive || webrtcSetupRef.current) return
    webrtcSetupRef.current = true

    setupWebRTC()

    return () => {
      if (peerConnectionRef.current) {
        peerConnectionRef.current.close()
        peerConnectionRef.current = null
      }
      if (localStreamRef.current) {
        localStreamRef.current.getTracks().forEach((track) => track.stop())
        localStreamRef.current = null
      }
    }
  }, [isCallActive])

  return (
    <div className="flex flex-col h-screen bg-gray-50">
      <header className="p-4">
        <Button variant="ghost" size="icon" onClick={endCall} className="text-gray-600">
          <ArrowLeft className="h-6 w-6" />
        </Button>
      </header>

      <div className="flex-1 flex flex-col items-center justify-center gap-6">
        <h1 className="text-2xl font-bold">{character.name}</h1>
        <div className="w-40 h-40 rounded-full overflow-hidden border-4 border-white shadow-lg">
          <img
            src={character.avatar || "/placeholder.svg"}
            alt={character.name}
            className="w-full h-full object-cover"
          />
        </div>
        <p className="text-gray-600 font-mono">Persona.ai</p>
        <p className="text-xl font-mono">{formatTime(callTime)}</p>
      </div>

      <footer className="p-8 flex justify-center gap-8">
        <Button variant="outline" size="icon" className="h-16 w-16 rounded-full bg-white">
          <Mic className="h-6 w-6" />
        </Button>
        <Button variant="destructive" size="icon" className="h-16 w-16 rounded-full" onClick={endCall}>
          <PhoneOff className="h-6 w-6" />
        </Button>
      </footer>

      <p className="text-center text-gray-400 pb-4">
        This is AI, and not a real person. Treat everything it says as fiction
      </p>
    </div>
  )
}
