// subscription_form.js
/*
 * Hanterar SMS-prenumerationsformuläret:
 * - Hämtar och fyller dropdowns för tidningar och län
 * - Validerar telefonnummer (+46-format) och obligatoriska fält
 * - Initierar och laddar Klarna-betalning
 * - Visar order-sammanfattning och hanterar betalningssvar
 */

/* ===================================================================================================
  Ladda listan av tidningar från servern och fyll <select>
=================================================================================================== */

// Hämta tidningar från servern och fylla en <select> med dem
async function loadNewspapers() {
  const select = document.getElementById("newspaper_id");
  try {
    const res = await fetch("/subscriptions/newspapers");
    if (!res.ok) throw new Error("Kunde inte hämta tidningar från servern");
    const newspapers = await res.json();
    select.innerHTML = "";
    const defaultOption = document.createElement("option");
    defaultOption.textContent = "Välj en tidning";
    defaultOption.disabled = true;
    defaultOption.selected = true;
    select.appendChild(defaultOption);
    Object.entries(newspapers).forEach(([id, name]) => {
      const option = document.createElement("option");
      option.value = id;
      option.textContent = name;
      select.appendChild(option);
    });
  } catch (err) {
    console.error("Kunde inte hämta tidningar:", err);
  }
}

/* ===================================================================================================
  Ladda listan av län från servern och fyll <select>
=================================================================================================== */

// Hämta län från servern och fylla en <select> med dem, utan dubbletter
async function loadCounties() {
  const select = document.getElementById("counties");
  try {
    const res = await fetch("/subscriptions/counties");
    if (!res.ok) throw new Error("Kunde inte hämta länslista");
    const counties = await res.json();
    select.innerHTML = "";
    const defaultOption = document.createElement("option");
    defaultOption.textContent = "Välj ett län";
    defaultOption.disabled = true;
    defaultOption.selected = true;
    select.appendChild(defaultOption);
    const added = new Set();
    Object.entries(counties).forEach(([code, name]) => {
      if (!added.has(name)) {
        added.add(name);
        const option = document.createElement("option");
        option.value = code;
        option.textContent = name;
        select.appendChild(option);
      }
    });
  } catch (err) {
    console.error("Kunde inte hämta länslista:", err);
  }
}
/* ===================================================================================================
// 3) Initiera dropdowns + “Gå till Klarna”-knapp på sidan laddning
=================================================================================================== */

// Ladda tidningar och län när sidan är klar
window.addEventListener("DOMContentLoaded", () => {
    // Ladda counties & newspapers som vanligt...
    loadCounties().then(() => {
      // Efter counties är inlästa, applicera förifyll:
      const preCounty = document.getElementById("county_prefill").value;
      if (preCounty) {
        Array.from(document.getElementById("counties").options)
             .find(opt => opt.value === preCounty)
             .selected = true;
      }
    });
    loadNewspapers().then(() => {
      const prePaper = document.getElementById("newspaper_prefill").value;
      if (prePaper) {
        document.getElementById("newspaper_id").value = prePaper;
      }
    });
    // Hämta mode från HTML
    const mode = document.getElementById("mode")?.value || "start";


// ÄNDRING: Ersatt ursprunglig go-to-klarna-btn-händelsehanterare för att visa modal
  document
    .getElementById("go-to-klarna-btn")
    .addEventListener("click", () => {
      // Visa bekräftelsemodalen
      const modal = new bootstrap.Modal(document.getElementById("klarnaConfirmModal"));
      modal.show();
    });
  // SLUT ÄNDRING

  // NY KOD: Lägg till händelsehanterare för "OK"-knappen i modalen
  document
    .getElementById("confirm-klarna-btn")
    .addEventListener("click", () => {
      // Stäng modalen
      const modal = bootstrap.Modal.getInstance(document.getElementById("klarnaConfirmModal"));
      modal.hide();

      // Scrolla ner till widgeten
      const klarnaContainer = document.getElementById("klarna-checkout-container");
      klarnaContainer.scrollIntoView({ behavior: "smooth" });

      // Initiera Klarna-betalning, skicka session-id, hämta authorization-token
      Klarna.Payments.authorize(
        { payment_method_category: "pay_now" },
        {},
        function (authRes) {
          if (authRes.approved) {
            // Skicka tillbaka till servern för bekräftelse
            const sessionId = localStorage.getItem("klarnaSessionId");
            fetch("/subscriptions/prenumeration-startad", {
              method: "POST",
              headers: { "Content-Type": "application/json" },
              body: JSON.stringify({
                session_id: sessionId,
                authorization_token: authRes.authorization_token,
                mode: mode,
              }),
            }).then(conf => {
              if (conf.redirected) {
                window.location.href = conf.url;
              } else {
                return conf.text().then(html => {
                  document.documentElement.innerHTML = html;
                });
              }
            });
          } else {
            document.getElementById("response").innerHTML =
              '<p class="error">Betalningen nekades.</p>';
          }
        }
      );
    });
  // SLUT NY KOD
});

/* ===================================================================================================
// 4) Hantera formulärets submit
=================================================================================================== */

 // Lyssna på formulärets submit, skicka data till servern, initiera Klarna-betalning
document
  .getElementById("subscription-form")
  .addEventListener("submit", async (event) => {
    event.preventDefault();

    // Hämta formuläret och dess element
    const form = event.target;
    const startBtn = form.querySelector("#start-sub-btn");
    const responseDiv = document.getElementById("response");
    const klarnaContainer = document.getElementById("klarna-checkout-container");
    const goToKlarnaContainer = document.getElementById("go-to-klarna-container");

    // Dölj “Gå till Klarna” tills load är klar
    goToKlarnaContainer.style.display = "none";

    // Tona ner startknappen under bearbetning
    startBtn.disabled = true;
    startBtn.style.opacity = "0.6";

    // Läs in fält
    let phoneNumber = form.querySelector("#phone_number").value.trim();
    const counties = Array.from(
      form.querySelector("#counties").selectedOptions
    ).map((o) => parseInt(o.value));
    const newspaperId = form.querySelector("#newspaper_id").value;

    // Normalisera till +46
    if (!phoneNumber.startsWith("+46")) {
      phoneNumber = phoneNumber.replace(/^0/, "+46");
    }

    // Validera telefonformat
    if (!/^\+46\d{9}$/.test(phoneNumber)) {
      responseDiv.innerHTML = `<p class="error">Ogiltigt telefonnummer. Använd formatet +46701234567.</p>`;
      startBtn.disabled = false;
      startBtn.style.opacity = "1";
      return;
    }

    // Kontrollera obligatoriska fält
    if (!phoneNumber || counties.length === 0 || !newspaperId) {
      responseDiv.innerHTML = `<p class="error">Vänligen fyll i telefonnummer, län och tidning.</p>`;
      startBtn.disabled = false;
      startBtn.style.opacity = "1";
      return;
    }

    try {
      // Skicka start-subscription
      const res = await fetch("/subscriptions/start-subscription", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          phone_number: phoneNumber,
          counties: counties,
          newspaper_id: parseInt(newspaperId),
        }),
      });
      const data = await res.json();

      // Felhantering, där det kastas ett felmeddelande om res.ok är falskt
      if (!res.ok) {
        if (data.error === "already_subscribed") {
          alert("Du är redan prenumerant med detta telefonnummer. Du dirigeras till din profil.");
          setTimeout(() => (window.location.href = "/users/profile"), 1000);
          return;
        }
        // Om det är ett ogiltigt telefonnummer kas
        responseDiv.innerHTML = `<p class="error">${data.error || "Okänt fel"}</p>`;
        startBtn.disabled = false;
        startBtn.style.opacity = "1";
        return;
      }

      // Spara session i localStorage
      localStorage.setItem("phoneNumber", phoneNumber);
      localStorage.setItem("klarnaSessionId", data.session_id);
      localStorage.setItem("email", data.email);

      // Visa order-sammanfattning för prenumerationen
      const countyText =
        form.querySelector("#counties").selectedOptions[0].textContent;
      const summaryHtml = `
        <div id="order-summary" class="order-summary-card mt-4">
          <h3>Din prenumeration</h3>
          <p>Du tecknar en SMS-prenumeration för 99 SEK i <strong>${countyText}</strong> för att få uppdateringar om trafikläget i ditt län.</p>
          <p>När du klickar på <em>"Gå till Klarna"</em> kommer du att dirigeras till Klarna för att slutföra betalningen.</p>
        </div>
      `;
      klarnaContainer.insertAdjacentHTML("beforebegin", summaryHtml);

      // Initiera & ladda Klarna
      Klarna.Payments.init({
        client_id: data.client_id,
        client_token: data.client_token,
      });
      // Ladda Klarna-widget
      Klarna.Payments.load(
        {
          container: "#klarna-checkout-container",
          payment_method_category: "pay_now",
        },
        (payRes) => {
          if (payRes.show_form) {
            // Visa “Gå till Klarna” om Klarna-widgeten är laddad korrekt
            goToKlarnaContainer.style.display = "block";
          } else if (payRes.error) {
            responseDiv.innerHTML = `<p class="error">Fel vid laddning: ${payRes.error}</p>`;
          }
        }
      );

      // Automatisk scroll till Klarna-widget
      setTimeout(() => {
        klarnaContainer.scrollIntoView({ behavior: "smooth" });
      }, 200);

      // Ändra “Starta” till “Ändra” med återställningslogik
      startBtn.textContent = "Ändra";
      startBtn.classList.replace("btn-primary", "btn-outline-primary");
      startBtn.disabled = false;
      startBtn.style.opacity = "1";
      startBtn.onclick = (e) => {
        e.preventDefault();
        // Rensa order-sammanfattning
        document.getElementById("order-summary")?.remove();
        klarnaContainer.innerHTML = "";
        goToKlarnaContainer.style.display = "none";
        responseDiv.innerHTML = "";
        form.reset();
        // Återställ knapp
        startBtn.textContent = "Starta prenumeration";
        startBtn.classList.replace("btn-outline-primary", "btn-primary");
        startBtn.onclick = null;
      };
      // Felhantering
    } catch (err) {
      console.error("Fetch error:", err);
      responseDiv.innerHTML = `<p class="error">Något gick fel: ${err.message}</p>`;
      startBtn.disabled = false;
      startBtn.style.opacity = "1";
    }
  });
