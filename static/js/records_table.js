$(document).ready(function () {
  let currentPage = 1;

  function fetchRecords(page = 1) {
    $.ajax({
      url: `/api/records/?page=${page}`,
      method: "GET",
      success: function (data) {
        const tbody = $("#myTable tbody");
        tbody.empty();

        if (data.results && data.results.length > 0) {
          data.results.forEach(function (record, index) {
            const row = $("<tr>");
            row.append($("<td>").text(((page - 1) * 7) + index + 1));
            row.append($("<td>").text(record.licenseplate_no || 'N/A'));
            row.append($("<td>").text(record.speed));
            row.append($("<td>").text(record.date));

            // Add status column
            const status = record.speed > 50 ? 'Exceeding' : 'Normal';
            const statusCell = $("<td>").text(status);
            if (status === 'Exceeding') {
              statusCell.addClass('exceeding-speed');
            }
            row.append(statusCell);

            tbody.append(row);
          });

          // Update pagination controls if they exist
          updatePaginationControls(data);
        } else {
          tbody.append(
            $("<tr>").append(
              $("<td>")
                .attr("colspan", "5")
                .text("No records found")
            )
          );
        }
      },
      error: function (error) {
        console.error("Error fetching records:", error);
        if (error.status === 401) {
          window.location.href = '/login/';  // Redirect to login page
        } else {
          const tbody = $("#myTable tbody");
          tbody.empty().append(
            $("<tr>").append(
              $("<td>")
                .attr("colspan", "5")
                .text("Error loading records. Please try again later.")
            )
          );
        }
      },
    });
  }

  function updatePaginationControls(data) {
    const paginationContainer = $(".table-footer");
    paginationContainer.empty();

    if (data.previous) {
      paginationContainer.append(
        $("<button>")
          .text("Previous")
          .addClass("pagination-btn")
          .click(() => {
            currentPage--;
            fetchRecords(currentPage);
          })
      );
    }

    if (data.next) {
      paginationContainer.append(
        $("<button>")
          .text("Next")
          .addClass("pagination-btn")
          .click(() => {
            currentPage++;
            fetchRecords(currentPage);
          })
      );
    }
  }

  // Initial fetch when the page loads
  fetchRecords();

  // Fetch records periodically (every 5 seconds to match cache duration)
  setInterval(() => fetchRecords(currentPage), 5000);
});
console.log(document.body.classList.contains('dark-mode')); // true or false
