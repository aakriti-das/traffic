$(document).ready(function () {
  function fetchRecords() {
    $.ajax({
      url: "/api/records/",
      method: "GET",
      success: function (data) {
        const lastFiveRecords = data.slice(-5);

        const tbody = $("#myTable tbody");
        tbody.empty();

        lastFiveRecords.forEach(function (record, index) {
          const row = $("<tr>");
          row.append($("<td>").text(index + 1));
          row.append($("<td>").text(record.licenseplate_no || 'N/A'));
          row.append($("<td>").text(record.speed || '0'));
          row.append($("<td>").text(record.date || 'N/A'));

          tbody.append(row);
        });

      },
      error: function (xhr, status, error) {
        console.log("Error fetching records:", {
          status: status,
          error: error,
          readyState: xhr.readyState
        });
      },
    });
  }

  // Initial fetch when the page loads
  fetchRecords();

  // Fetch records periodically (e.g., every 2 seconds) for real-time updates
  setInterval(fetchRecords, 2000); // Increased interval to reduce server load
});