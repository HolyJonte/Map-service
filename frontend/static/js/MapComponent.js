import { CameraLayer } from './CameraLayer.js';  // Se till att sökvägen är korrekt

class MapComponent extends HTMLElement {
  constructor() {
    super();
    this.map = null;
    this.cameraLayer = null;
  }

  connectedCallback() {
    this.innerHTML = `<div id="map" style="height: 80vh;"></div>`;
    this.initMap();
  }

  initMap() {
    this.map = L.map('map', {
      center: [62.0, 15.0],  // Centrera kartan på Sverige
      zoom: 6                // Zoomnivå för att visa Sverige
    });

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '© OpenStreetMap contributors',
      maxZoom: 18
    }).addTo(this.map);

    // Skapa fartkameralagret och ladda datan
    this.cameraLayer = new CameraLayer(this.map);
    this.cameraLayer.loadData();
  }
}

customElements.define('map-component', MapComponent);
