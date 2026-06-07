using UnityEngine;

namespace NeuroAR.Network
{
    [RequireComponent(typeof(LineRenderer))]
    public class ConnectionVisual : MonoBehaviour
    {
        [Header("Références")]
        public Transform neuronA;
        public Transform neuronB;

        [Header("Apparence")]
        public float minWidth = 0.002f;
        public float maxWidth = 0.015f;
        public float weight = 0f;

        [Header("Animation")]
        public float flowSpeed = 1f;
        public bool isAnimating = false;

        private LineRenderer _lineRenderer;
        private Material _material;

        void Awake()
        {
            _lineRenderer = GetComponent<LineRenderer>();
            _lineRenderer.positionCount = 2;
            _lineRenderer.useWorldSpace = true;
            _material = _lineRenderer.material;
        }

        void Update()
        {
            if (neuronA == null || neuronB == null) return;

            _lineRenderer.SetPosition(0, neuronA.position);
            _lineRenderer.SetPosition(1, neuronB.position);

            UpdateWidth();

            if (isAnimating)
                AnimateFlow();
        }

        private void UpdateWidth()
        {
            float absWeight = Mathf.Abs(weight);
            float w = Mathf.Lerp(minWidth, maxWidth, absWeight);
            _lineRenderer.startWidth = w;
            _lineRenderer.endWidth = w * 0.5f;
        }

        private void AnimateFlow()
        {
            float offset = Time.time * flowSpeed;
            _material.SetTextureOffset("_MainTex", new Vector2(offset, 0));
        }

        public void SetWeight(float w)
        {
            weight = Mathf.Clamp(w, -1f, 1f);

            // Couleur selon signe du poids
            Color positive = new Color(0.2f, 0.8f, 1f); // bleu cyan
            Color negative = new Color(1f, 0.3f, 0.3f); // rouge
            Color zero     = new Color(0.5f, 0.5f, 0.5f); // gris

            Color target = w > 0
                ? Color.Lerp(zero, positive, w)
                : Color.Lerp(zero, negative, -w);

            _material.color = target;
            _material.SetColor("_EmissionColor", target * 0.5f);
        }

        public void AnimateActivation(float duration = 0.5f)
        {
            isAnimating = true;
            Invoke(nameof(StopAnimation), duration);
        }

        private void StopAnimation() => isAnimating = false;
    }
}