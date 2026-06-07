using UnityEngine;
using System;
using System.Threading.Tasks;
using NativeWebSocket;

namespace NeuroAR.Communication
{
    public class WebSocketClient : MonoBehaviour
    {
        [Header("Config")]
        public string serverUrl = "ws://192.168.1.1:8000/ws";
        public float reconnectDelay = 3f;
        public bool autoConnect = true;

        private WebSocket _socket;
        private bool _isReconnecting = false;

        // Events
        public event Action OnConnected;
        public event Action OnDisconnected;
        public event Action<string> OnMessageReceived;
        public event Action<string> OnError;

        public bool IsConnected => _socket?.State == WebSocketState.Open;

        async void Start()
        {
            if (autoConnect)
                await Connect();
        }

        public async Task Connect()
        {
            if (_socket != null && _socket.State == WebSocketState.Open)
                return;

            _socket = new WebSocket(serverUrl);

            _socket.OnOpen += () =>
            {
                Debug.Log("[WebSocket] Connecté au serveur");
                OnConnected?.Invoke();
                _isReconnecting = false;
            };

            _socket.OnClose += (code) =>
            {
                Debug.Log($"[WebSocket] Déconnecté : {code}");
                OnDisconnected?.Invoke();
                if (!_isReconnecting)
                    _ = Reconnect();
            };

            _socket.OnMessage += (bytes) =>
            {
                string message = System.Text.Encoding.UTF8.GetString(bytes);
                OnMessageReceived?.Invoke(message);
            };

            _socket.OnError += (error) =>
            {
                Debug.LogError($"[WebSocket] Erreur : {error}");
                OnError?.Invoke(error);
            };

            await _socket.Connect();
        }

        void Update()
        {
#if !UNITY_WEBGL || UNITY_EDITOR
            _socket?.DispatchMessageQueue();
#endif
        }

        public async Task Send(string message)
        {
            if (!IsConnected)
            {
                Debug.LogWarning("[WebSocket] Pas connecté");
                return;
            }
            await _socket.SendText(message);
        }

        private async Task Reconnect()
        {
            _isReconnecting = true;
            Debug.Log($"[WebSocket] Reconnexion dans {reconnectDelay}s...");
            await Task.Delay(TimeSpan.FromSeconds(reconnectDelay));
            await Connect();
        }

        async void OnDestroy()
        {
            if (_socket != null)
                await _socket.Close();
        }

        async void OnApplicationPause(bool pause)
        {
            if (pause)
            {
                if (_socket != null)
                    await _socket.Close();
            }
            else
            {
                await Connect();
            }
        }
    }
}