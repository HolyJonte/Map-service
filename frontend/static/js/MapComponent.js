class MapComponent extends HTMLElement {
  constructor() {
    super();
    this.map = null;
  }

  connectedCallback() {
    this.innerHTML = `<div id="map"></div>`;
    this.initMap();  // <- här!
  }

  initMap() {
    this.map = L.map('map').setView([62.0, 15.0], 5); // Centrera över Sverige

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '© OpenStreetMap contributors',
      maxZoom: 18
    }).addTo(this.map);
  }
}

customElements.define('map-component', MapComponent);

