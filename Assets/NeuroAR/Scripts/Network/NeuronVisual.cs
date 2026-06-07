using UnityEngine;
using System.Collections;

namespace NeuroAR.Network
{
    public class NeuronVisual : MonoBehaviour
    {
        [Header("Materials")]
        public Material materialInput;
        public Material materialHidden;
        public Material materialOutput;
        public Material materialActive;

        [Header("Animation")]
        public float pulseSpeed = 2f;
        public float pulseIntensity = 0.3f;
        public float activationDuration = 0.5f;

        [Header("Info")]
        public int layerIndex;
        public int neuronIndex;
        public float activationValue;

        private Renderer _renderer;
        private Material _currentMaterial;
        private Material _baseMaterial;
        private bool _isActivating = false;

        public enum NeuronType { Input, Hidden, Output }
        public NeuronType neuronType;

        void Awake()
        {
            _renderer = GetComponent<Renderer>();
        }

        void Start()
        {
            SetType(neuronType);
            StartCoroutine(PulseRoutine());
        }

        public void SetType(NeuronType type)
        {
            neuronType = type;
            _baseMaterial = type switch
            {
                NeuronType.Input  => materialInput,
                NeuronType.Output => materialOutput,
                _                 => materialHidden
            };
            _renderer.material = _baseMaterial;
            _currentMaterial = _renderer.material;
        }

        public void Activate(float value)
        {
            activationValue = value;
            if (!_isActivating)
                StartCoroutine(ActivationRoutine(value));
        }

        private IEnumerator ActivationRoutine(float value)
        {
            _isActivating = true;
            _renderer.material = materialActive;

            // Scale pop
            float t = 0f;
            Vector3 baseScale = Vector3.one;
            Vector3 targetScale = Vector3.one * (1f + value * 0.4f);

            while (t < activationDuration)
            {
                t += Time.deltaTime;
                float progress = t / activationDuration;
                float curve = Mathf.Sin(progress * Mathf.PI);
                transform.localScale = Vector3.Lerp(baseScale, targetScale, curve);
                yield return null;
            }

            transform.localScale = baseScale;
            _renderer.material = _currentMaterial;
            _isActivating = false;
        }

        private IEnumerator PulseRoutine()
        {
            while (true)
            {
                float t = Mathf.Sin(Time.time * pulseSpeed) * pulseIntensity;
                if (_currentMaterial != null)
                {
                    Color emission = _currentMaterial.GetColor("_EmissionColor");
                    _currentMaterial.SetColor("_EmissionColor", emission * (1f + t));
                }
                yield return new WaitForSeconds(0.05f);
            }
        }

        public void SetActivationValue(float value)
        {
            activationValue = Mathf.Clamp01(value);
            Color baseColor = _baseMaterial.color;
            _currentMaterial.color = Color.Lerp(baseColor, materialActive.color, activationValue);
        }
    }
}