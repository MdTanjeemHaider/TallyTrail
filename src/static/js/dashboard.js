// On page load get transactions from server to display them in a table and graphs
window.onload = function() {
    // Get data from server
    fetch('/api/get_transactions')
    .then(response => response.json())
    .then(data => {
        // Update the table
        updateTable(data.transactions);

        // Draw graphs
        drawGraphs(data.transactions);
    }).catch(error => console.error('Error fetching transactions:', error));
}

function updateTable(transactions) {
    const table = document.getElementById("transaction_table");
    table.innerHTML = ""; // Clear the table

    transactions.forEach(transaction => {
        // Create a row
        const row = document.createElement('tr');

        // Set color based on transaction amount
        const color = transaction.amount < 0 ? 'red' : 'green';

        // Create cells
        const date_cell = document.createElement('td');
        date_cell.textContent = new Date(transaction.date).toLocaleDateString();
        date_cell.style.backgroundColor = color;

        const name_cell = document.createElement('td');
        name_cell.textContent = transaction.name;
        name_cell.style.backgroundColor = color;

        const amount_cell = document.createElement('td');
        amount_cell.textContent = transaction.amount;
        amount_cell.style.backgroundColor = color;

        const recurring_cell = document.createElement('td');
        recurring_cell.textContent = transaction.recurring ? 'Recurring' : 'One time';
        recurring_cell.style.backgroundColor = color;

        const delete_cell = document.createElement('td');
        const delete_button = document.createElement('button');
        delete_button.textContent = "🗑️";
        delete_button.onclick = function () {
            deleteTransaction(transaction.id);
        }
        delete_cell.appendChild(delete_button);
        delete_cell.style.backgroundColor = color;

        // Append cells to row
        row.appendChild(date_cell);
        row.appendChild(name_cell);
        row.appendChild(amount_cell);
        row.appendChild(recurring_cell);
        row.appendChild(delete_cell);

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

    let total_balance = 0;

    transactions.forEach(transactions => {
        const date = new Date(transactions.date).toLocaleDateString();
        total_balance += transactions.amount;

        dates.push(date);
        balance.push(total_balance);

        if (transactions.amount < 0) {
            spending.push(transactions.amount);
            income.push(0);
        } else {
            income.push(transactions.amount);
            spending.push(0);
        }
    });

    // Render graphs
    renderGraph('spending_graph', 'Spending ($)', dates, spending);
    renderGraph('balance_graph', 'Balance ($)', dates, balance);
    renderGraph('income_graph', 'Income ($)', dates, income);
}

// Render a graph on a canvas
function renderGraph(canvas_id, title, labels, data) {
    const context = document.getElementById(canvas_id).getContext('2d');
    new Chart(context, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: title,
                data: data,
                backgroundColor: 'rgba(255, 255, 255, 255)',
                borderColor: 'rgba(0, 0, 0, 255)',
                borderWidth: 1
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
                        text: title
                    },

                },
                x: {
                    title: {
                        display: true,
                        text: 'Date'
                    }
                }
            }
        }
    });
}

function deleteTransaction(transaction_id) {
    // Send delete request to server
    fetch(`/delete_transaction/${transaction_id}`,{method: 'DELETE'}).then(response => {
        // Reload page
        window.location.reload();
    });
}