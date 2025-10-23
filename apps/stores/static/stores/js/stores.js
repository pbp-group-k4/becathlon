document.addEventListener("DOMContentLoaded", () => {
  const searchInput = document.getElementById("storeSearch");
  const searchBtn = document.getElementById("searchBtn");
  const resultsContainer = document.getElementById("resultsContainer");

  async function searchStores() {
    const q = searchInput.value.trim();
    if (!q) {
      resultsContainer.innerHTML = `<p class="no-results">Enter a search keyword to find stores.</p>`;
      return;
    }

    try {
      const response = await fetch(`/stores/api/?q=${encodeURIComponent(q)}`);
      const data = await response.json();

      if (data.results.length === 0) {
        resultsContainer.innerHTML = `<p class="no-results">No stores found for "${q}".</p>`;
        return;
      }

      resultsContainer.innerHTML = data.results.map(store => `
        <div class="store-card">
          <h3>${store.name}</h3>
          <p><strong>Address:</strong> ${store.address}</p>
          <p><strong>City:</strong> ${store.city}</p>
          <p><strong>Country:</strong> ${store.country}</p>
          <a href="/stores/${store.id}/">View Details →</a>
        </div>
      `).join("");

    } catch (error) {
      console.error("Error fetching stores:", error);
      resultsContainer.innerHTML = `<p class="no-results">Error fetching results.</p>`;
    }
  }

  searchBtn.addEventListener("click", searchStores);
  searchInput.addEventListener("keydown", (e) => {
    if (e.key === "Enter") {
      e.preventDefault();
      searchStores();
    }
  });
});
