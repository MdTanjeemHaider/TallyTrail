// On page load, fetch transactions from the server to display in the table and graphs
window.onload = function () {
    fetch('/get_transactions')
        .then(response => response.json())
        .then(data => {
            updateTable(data.transactions); // Populate table with transactions
            sortTable(document.querySelector('th[data-column="date"]')); // Default sort by date
            drawGraphs(data.transactions); // Draw spending, balance, and income graphs
            console.log(data.transactions); // Log transactions for debugging
        })
        .catch(error => console.error('Error fetching transactions:', error));
};

/**
 * Updates the transaction table with data
 * @param {Array} transactions - List of transaction objects
 */
function updateTable(transactions) {
    const table = document.getElementById("transaction-table");
    table.innerHTML = ""; // Clear existing table content

    transactions.forEach(transaction => {
        const row = document.createElement('tr');
        const color = transaction.amount < 0 ? 'darkred' : 'green'; // Red for spending, green for income

        // Create cells
        row.appendChild(createCell(new Date(transaction.date).toLocaleDateString(), color));
        row.appendChild(createCell(transaction.name, color));
        row.appendChild(createCell(transaction.amount, color));
        row.appendChild(createCell(transaction.description, color));

        // Delete button cell
        const deleteCell = document.createElement('td');
        const deleteButton = document.createElement('button');
        deleteButton.innerHTML = '<span class="delete-icon">🗑️</span>';
        deleteButton.onclick = () => deleteTransaction(transaction.id);
        deleteButton.style.backgroundColor = color;
        deleteCell.appendChild(deleteButton);
        deleteCell.style.backgroundColor = color;
        row.appendChild(deleteCell);

        table.appendChild(row); // Add row to table
    });
}

/**
 * Helper function to create a table cell
 * @param {string} text - Cell content
 * @param {string} color - Background color
 */
function createCell(text, color) {
    const cell = document.createElement('td');
    cell.textContent = text;
    cell.style.backgroundColor = color;
    return cell;
}

/**
 * Draws spending, income, and balance graphs
 * @param {Array} transactions - List of transaction objects
 */
function drawGraphs(transactions) {
    // Sort transactions by date
    transactions.sort((a, b) => new Date(a.date) - new Date(b.date));

    const spending = [], income = [], balance = [], dates = [];
    let totalBalance = 0;

    transactions.forEach(transaction => {
        const date = new Date(transaction.date).toLocaleDateString();
        totalBalance += transaction.amount;

        dates.push(date);
        balance.push(totalBalance);
        spending.push(transaction.amount < 0 ? transaction.amount : 0);
        income.push(transaction.amount > 0 ? transaction.amount : 0);
    });

    renderGraph('spending-graph', 'Spending ($)', dates, spending);
    renderGraph('balance-graph', 'Balance ($)', dates, balance);
    renderGraph('income-graph', 'Income ($)', dates, income);
}

/**
 * Renders a graph on a specified canvas
 * @param {string} canvasId - ID of the canvas element
 * @param {string} title - Title of the graph
 * @param {Array} labels - Labels for the graph
 * @param {Array} data - Data points for the graph
 */
function renderGraph(canvasId, title, labels, data) {
    const context = document.getElementById(canvasId).getContext('2d');
    new Chart(context, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: title,
                data: data,
                borderColor: 'rgba(255, 255, 255, 1)',
                borderWidth: 2,
            }]
        },
        options: {
            plugins: { legend: { display: false } },
            scales: {
                y: {
                    title: { display: true, text: title, color: 'white' },
                    grid: { color: 'white' },
                    ticks: { color: 'white' }
                },
                x: {
                    title: { display: true, text: 'Date', color: 'white' },
                    grid: { color: 'white' },
                    ticks: { color: 'white' }
                }
            }
        }
    });
}

/**
 * Filters the transaction table based on user input
 */
function filterTable() {
    const input = document.getElementById('search-input').value.toLowerCase();
    const rows = Array.from(document.querySelectorAll('#transaction-table tr'));

    rows.forEach(row => {
        const transactionName = row.children[1].textContent.toLowerCase();
        const description = row.children[3].textContent.toLowerCase();
        row.style.display = transactionName.includes(input) || description.includes(input) ? '' : 'none';
    });
}

/**
 * Sorts the transaction table by a specified column
 * @param {HTMLElement} header - Header cell clicked for sorting
 */
function sortTable(header) {
    const table = document.getElementById('transaction-table');
    const rows = Array.from(table.querySelectorAll('tr'));
    const columnIndex = Array.from(header.parentNode.children).indexOf(header);
    const isAscending = header.getAttribute('data-order') === 'asc';

    header.parentNode.querySelectorAll('th').forEach(th => th.removeAttribute('data-order'));
    header.setAttribute('data-order', isAscending ? 'desc' : 'asc');

    rows.sort((a, b) => {
        const aValue = a.children[columnIndex].textContent.trim();
        const bValue = b.children[columnIndex].textContent.trim();
        return isNaN(aValue) && isNaN(bValue)
            ? isAscending ? aValue.localeCompare(bValue) : bValue.localeCompare(aValue)
            : isAscending ? aValue - bValue : bValue - aValue;
    });

    rows.forEach(row => table.appendChild(row));
}

/**
 * Deletes a transaction by ID
 * @param {number} transactionId - ID of the transaction to delete
 */
function deleteTransaction(transactionId) {
    fetch(`/delete_transaction/${transactionId}`, { method: 'DELETE' })
        .then(response => window.location.href = response.url)
        .catch(error => console.error('Error deleting transaction:', error));
}

/**
 * Opens the modal
 */
function openModal() {
    document.getElementById("modal").style.display = "flex";
}

/**
 * Closes the modal
 */
function closeModal() {
    document.getElementById("modal").style.display = "none";
}

// Closes modal when clicking outside it
window.onclick = function (event) {
    const modal = document.getElementById("modal");
    if (event.target === modal) {
        closeModal();
    }
};

/**
 * Logs the user out by clearing the session
 */
function logout() {
    fetch('/logout', { method: 'POST' })
        .then(response => window.location.href = response.url)
        .catch(error => console.error('Error logging out:', error));
}