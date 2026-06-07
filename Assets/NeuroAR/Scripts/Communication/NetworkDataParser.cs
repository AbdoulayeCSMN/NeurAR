using UnityEngine;
using Newtonsoft.Json;
using NeuroAR.Network;
using NeuroAR.AR;

namespace NeuroAR.Communication
{
    public class NetworkDataParser : MonoBehaviour
    {
        [Header("Références")]
        public WebSocketClient webSocketClient;
        public ARPlacementManager placementManager;

        private NetworkRenderer _networkRenderer;
        private NetworkData _pendingData;
        private bool _networkBuilt = false;

        void Start()
        {
            webSocketClient.OnConnected       += HandleConnected;
            webSocketClient.OnDisconnected    += HandleDisconnected;
            webSocketClient.OnMessageReceived += HandleMessage;
            webSocketClient.OnError           += HandleError;
        }

        void Update()
        {
            // Attend le placement AR puis applique les données en attente
            if (!_networkBuilt && _pendingData != null && placementManager.IsPlaced)
            {
                GameObject networkObj = placementManager.GetSpawnedNetwork();
                if (networkObj != null)
                {
                    _networkRenderer = networkObj.GetComponent<NetworkRenderer>();
                    if (_networkRenderer != null)
                    {
                        _networkRenderer.BuildNetwork(_pendingData);
                        _networkBuilt = true;
                        _pendingData  = null;
                        Debug.Log("[Parser] Réseau construit après placement AR ✅");
                    }
                }
            }
        }

        private void HandleConnected()
        {
            Debug.Log("[Parser] WebSocket connecté ✅");
            _ = webSocketClient.Send("{\"action\":\"get_network\"}");
        }

        private void HandleDisconnected()
        {
            Debug.Log("[Parser] WebSocket déconnecté");
            _networkBuilt = false;
        }

        private void HandleMessage(string json)
        {
            try
            {
                NetworkData data = JsonConvert.DeserializeObject<NetworkData>(json);
                if (data == null) return;

                UnityMainThreadDispatcher.Instance.Enqueue(() =>
                {
                    ProcessNetworkData(data);
                });
            }
            catch (System.Exception e)
            {
                Debug.LogError($"[Parser] Erreur parsing JSON : {e.Message}");
            }
        }

        private void ProcessNetworkData(NetworkData data)
        {
            // Réseau pas encore placé → on met en attente
            if (!placementManager.IsPlaced)
            {
                _pendingData = data;
                Debug.Log("[Parser] Données reçues, en attente du placement AR...");
                return;
            }

            GameObject networkObj = placementManager.GetSpawnedNetwork();
            if (networkObj == null) return;

            if (_networkRenderer == null)
                _networkRenderer = networkObj.GetComponent<NetworkRenderer>();

            if (_networkRenderer == null) return;

            if (data.phase == "init" || !_networkBuilt)
            {
                _networkRenderer.BuildNetwork(data);
                _networkBuilt = true;
                Debug.Log("[Parser] Réseau initialisé ✅");
            }
            else
            {
                _networkRenderer.UpdateNetwork(data);
                Debug.Log($"[Parser] Réseau mis à jour — phase : {data.phase}");
            }
        }

        private void HandleError(string error)
        {
            Debug.LogError($"[Parser] Erreur WebSocket : {error}");
        }

        public void OnNetworkReset()
        {
            _networkBuilt = false;
            _pendingData  = null;
        }
    }
}