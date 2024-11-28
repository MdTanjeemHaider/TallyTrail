// On page load get transactions from server to display them in a table and graphs
window.onload = function() {
    // Get data from server
    fetch('/get_transactions')
    .then(response => response.json())
    .then(data => {
        // Update the table
        updateTable(data.transactions);

        // Sort table by date
        sortTable(document.querySelector('th[data-column="date"]'));

        // Draw graphs
        drawGraphs(data.transactions);

        console.log(data.transactions);
    }).catch(error => console.error('Error fetching transactions:', error));
}

function updateTable(transactions) {
    const table = document.getElementById("transaction-table");
    table.innerHTML = ""; // Clear the table

    transactions.forEach(transaction => {
        // Create a row
        const row = document.createElement('tr');

        // Set color based on transaction amount
        const color = transaction.amount < 0 ? 'darkred' : 'green';

        // Create cells

        // Date cell
        const dateCell = document.createElement('td');
        dateCell.textContent = new Date(transaction.date).toLocaleDateString();
        dateCell.style.backgroundColor = color;

        // Name cell
        const nameCell = document.createElement('td');
        nameCell.textContent = transaction.name;
        nameCell.style.backgroundColor = color;

        // Amount cell
        const amountCell = document.createElement('td');
        amountCell.textContent = transaction.amount;
        amountCell.style.backgroundColor = color;

        // Description cell
        const descriptionCell = document.createElement('td');
        descriptionCell.textContent = transaction.description;
        descriptionCell.style.backgroundColor = color;

        // Delete cell
        const deleteCell = document.createElement('td');
        const deleteButton = document.createElement('button');
        deleteButton.innerHTML = '<span class="delete-icon">🗑️</span>';
        deleteButton.onclick = function () {
            deleteTransaction(transaction.id);
        }
        deleteButton.style.backgroundColor = color;
        deleteCell.appendChild(deleteButton);
        deleteCell.style.backgroundColor = color;

        // Append cells to row
        row.appendChild(dateCell);
        row.appendChild(nameCell);
        row.appendChild(amountCell);
        row.appendChild(descriptionCell);
        row.appendChild(deleteCell);

        // Append row to table
        table.appendChild(row);
    });
}

function drawGraphs(transactions) {
    // Sort transactions by date
    transactions.sort((a, b) => new Date(a.date) - new Date(b.date));

    // Prepare data for graphs
    const spending = [];
    const income = [];
    const balance = [];
    const dates = [];

    let totalBalance = 0;

    transactions.forEach(transactions => {
        const date = new Date(transactions.date).toLocaleDateString();
        totalBalance += transactions.amount;

        dates.push(date);
        balance.push(totalBalance);

        if (transactions.amount < 0) {
            spending.push(transactions.amount);
            income.push(0);
        } else {
            income.push(transactions.amount);
            spending.push(0);
        }
    });

    // Render graphs
    renderGraph('spending-graph', 'Spending ($)', dates, spending);
    renderGraph('balance-graph', 'Balance ($)', dates, balance);
    renderGraph('income-graph', 'Income ($)', dates, income);
}

// Render a graph on a canvas
function renderGraph(canvasId, title, labels, data) {
    const context = document.getElementById(canvasId).getContext('2d');
    new Chart(context, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: title,
                data: data,
                backgroundColor: 'rgba(255, 255, 255, 255)',
                borderColor:'rgba(255, 255, 255, 255)',
                borderWidth: 2
            }]
        },
        options: {
            plugins: {
                legend: {
                    display: false
                }
            },
            scales: {
                y: {
                    title: {
                        display: true,
                        text: title,
                        color: 'rgba(255, 255, 255, 255)'
                    },
                    grid: {
                        color: 'rgba(255, 255, 255, 255)'
                    },
                    ticks: {
                        color: 'rgba(255, 255, 255, 255)'
                    }
                },
                x: {
                    title: {
                        display: true,
                        text: 'Date',
                        color: 'rgba(255, 255, 255, 255)'
                    },
                    grid: {
                        color: 'rgba(255, 255, 255, 255)'
                    },
                    ticks: {
                        color: 'rgba(255, 255, 255, 255)'
                    }
                }
            }
        }
    });
}

function filterTable() {
    const input = document.getElementById('search-input');
    const table = document.getElementById('transaction-table');
    const rows = Array.from(table.querySelectorAll('tr'));

    rows.forEach(row => {
        const transactionName = row.children[1].textContent.toLowerCase();
        const description = row.children[3].textContent.toLowerCase();

        if (transactionName.includes(input.value.toLowerCase()) || description.includes(input.value.toLowerCase())) {
            row.style.display = ''; // Show row
        } else {
            row.style.display = 'none'; // Hide row
        }

    })
}

function sortTable(header) {
    const table = document.getElementById('transaction-table');
    const rows = Array.from(table.querySelectorAll('tr')); // Get all table rows
    const columnIndex = Array.from(header.parentNode.children).indexOf(header); // Get column index
    const isAscending = header.getAttribute('data-order') === 'asc'; // Check current sort order

    // Clear sort indicators on all headers
    header.parentNode.querySelectorAll('th').forEach(th => th.removeAttribute('data-order'));

    // Set sort order for the clicked column
    header.setAttribute('data-order', isAscending ? 'desc' : 'asc');

    // Sort rows
    const sortedRows = rows.sort((a, b) => {
        const aValue = a.children[columnIndex].textContent.trim();
        const bValue = b.children[columnIndex].textContent.trim();

        if (isNaN(aValue) && isNaN(bValue)) {
            return isAscending
            ? aValue.localeCompare(bValue)
            : bValue.localeCompare(aValue);
        } else {
            return isAscending ? aValue - bValue : bValue - aValue;
        }
    });

    // Append sorted rows back to the table body
    sortedRows.forEach(row => table.appendChild(row));
}



function deleteTransaction(transactionId) {
    // Send delete request to server
    fetch(`/delete_transaction/${transactionId}`,{method: 'DELETE'}).then(response => {
        // Reload page
        window.location.href = response.url;
    });
}

function openModal() {
    document.getElementById("modal").style.display = "flex"; // Show modal
}

function closeModal() {
    document.getElementById("modal").style.display = "none"; // Hide modal
}

window.onclick = function(event) {
    const modal = document.getElementById("modal");
    if (event.target == modal) {
        modal.style.display = "none"; // Hide modal if clicked outside
    }
}

function logout() {
    fetch('/logout', {method: 'POST'}).then(response => {
        window.location.href = response.url;
    })
}