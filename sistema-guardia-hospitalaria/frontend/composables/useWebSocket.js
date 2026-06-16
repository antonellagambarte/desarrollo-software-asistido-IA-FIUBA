import { onMounted, onUnmounted } from 'vue'

export function useWebSocket(onMessage) {
  let ws = null
  let reconnectTimeout = null

  function connect() {
    ws = new WebSocket('ws://localhost:8000/ws')

    ws.onmessage = () => onMessage()

    ws.onclose = () => {
      reconnectTimeout = setTimeout(connect, 3000)
    }

    ws.onerror = () => {
      ws.close()
    }
  }

  onMounted(connect)

  onUnmounted(() => {
    clearTimeout(reconnectTimeout)
    ws?.close()
  })
}
