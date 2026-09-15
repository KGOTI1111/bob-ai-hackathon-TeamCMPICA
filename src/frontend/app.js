// Supply Chain Optimizer Dashboard - JavaScript
const API_BASE_URL = 'http://localhost:8000/api';

// State management
const state = {
    shipments: [],
    disruptions: [],
    fleetAssets: [],
    temperatureAlerts: [],
    sensorReadings: []
};

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    setupEventListeners();
    loadDashboardData();
    refreshData(); // Initial load
    
    // Auto-refresh every 30 seconds
    setInterval(refreshData, 30000);
});

// Event Listeners
function setupEventListeners() {
    // Tab Navigation
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            const tabName = e.target.dataset.tab;
            switchTab(tabName);
        });
    });

    // Filters for Shipments
    document.getElementById('status-filter').addEventListener('change', filterShipments);
    document.getElementById('cold-chain-filter').addEventListener('change', filterShipments);
    document.getElementById('shipment-search').addEventListener('input', filterShipments);

    // Filters for Disruptions
    document.getElementById('disruption-severity').addEventListener('change', filterDisruptions);
    document.getElementById('active-only').addEventListener('change', filterDisruptions);

    // Filters for Fleet
    document.getElementById('asset-type-filter').addEventListener('change', filterFleet);
    document.getElementById('asset-status-filter').addEventListener('change', filterFleet);
    document.getElementById('cold-chain-asset-filter').addEventListener('change', filterFleet);

    // Filters for Cold Chain
    document.getElementById('alert-severity-filter').addEventListener('change', filterTemperatureAlerts);
    document.getElementById('unacknowledged-only').addEventListener('change', filterTemperatureAlerts);
    document.getElementById('cold-shipment-search').addEventListener('input', filterTemperatureAlerts);
}

// Tab Switching
function switchTab(tabName) {
    // Hide all tabs
    document.querySelectorAll('.tab-content').forEach(tab => {
        tab.classList.remove('active');
    });
    
    // Remove active class from all buttons
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('active');
    });

    // Show selected tab
    document.getElementById(tabName).classList.add('active');
    
    // Add active class to clicked button
    event.target.classList.add('active');

    // Load tab-specific data
    switch(tabName) {
        case 'shipments':
            displayShipments();
            break;
        case 'disruptions':
            displayDisruptions();
            break;
        case 'fleet':
            displayFleet();
            break;
        case 'cold-chain':
            displayColdChainAlerts();
            displaySensorReadings();
            break;
    }
}

// Data Refresh
async function refreshData() {
    try {
        await Promise.all([
            loadShipments(),
            loadDisruptions(),
            loadFleetAssets(),
            loadTemperatureAlerts(),
            loadSensorReadings()
        ]);
        
        // Update active tab
        const activeTab = document.querySelector('.tab-content.active').id;
        if (activeTab === 'dashboard') {
            loadDashboardData();
        }
        
        updateAPIStatus(true);
    } catch (error) {
        console.error('Error refreshing data:', error);
        updateAPIStatus(false);
    }
}

// Dashboard Data
async function loadDashboardData() {
    try {
        const [shipmentSummary, disruptionSummary, fleetSummary] = await Promise.all([
            fetch(`${API_BASE_URL}/shipments/summary/dashboard`).then(r => r.json()),
            fetch(`${API_BASE_URL}/disruptions/summary/dashboard`).then(r => r.json()),
            fetch(`${API_BASE_URL}/fleet/summary/dashboard`).then(r => r.json())
        ]);

        // Update shipment KPIs
        document.getElementById('total-shipments').textContent = shipmentSummary.total_shipments;
        document.getElementById('in-transit').textContent = shipmentSummary.in_transit;
        document.getElementById('delayed').textContent = shipmentSummary.delayed;
        document.getElementById('delivered').textContent = shipmentSummary.delivered;
        document.getElementById('cold-chain-count').textContent = shipmentSummary.cold_chain_shipments;
        document.getElementById('high-risk').textContent = shipmentSummary.high_risk_shipments;

        // Update disruption KPIs
        document.getElementById('active-disruptions').textContent = disruptionSummary.active_disruptions;
        document.getElementById('affected-count').textContent = disruptionSummary.total_affected_shipments;
        document.getElementById('critical-disruptions').textContent = disruptionSummary.critical_disruptions;
        document.getElementById('regions-affected').textContent = disruptionSummary.regions_affected.length;

        // Update fleet KPIs
        document.getElementById('total-assets').textContent = fleetSummary.total_assets;
        document.getElementById('idle-assets').textContent = fleetSummary.idle_assets;
        document.getElementById('fleet-in-transit').textContent = fleetSummary.in_transit;
        document.getElementById('cold-capable').textContent = fleetSummary.cold_chain_capable;

        // Load alert summaries
        loadCriticalAlerts();
        loadActiveDisruptionsList();
    } catch (error) {
        console.error('Error loading dashboard data:', error);
    }
}

// Load Shipments
async function loadShipments() {
    try {
        const response = await fetch(`${API_BASE_URL}/shipments/`);
        state.shipments = await response.json();
    } catch (error) {
        console.error('Error loading shipments:', error);
    }
}

// Load Disruptions
async function loadDisruptions() {
    try {
        const response = await fetch(`${API_BASE_URL}/disruptions/`);
        state.disruptions = await response.json();
    } catch (error) {
        console.error('Error loading disruptions:', error);
    }
}

// Load Fleet Assets
async function loadFleetAssets() {
    try {
        const response = await fetch(`${API_BASE_URL}/fleet/`);
        state.fleetAssets = await response.json();
    } catch (error) {
        console.error('Error loading fleet assets:', error);
    }
}

// Load Temperature Alerts
async function loadTemperatureAlerts() {
    try {
        const response = await fetch(`${API_BASE_URL}/cold-chain/alerts`);
        state.temperatureAlerts = await response.json();
        
        // Update alert count
        const criticalCount = state.temperatureAlerts.filter(a => a.severity === 'critical').length;
        document.getElementById('critical-alerts').textContent = criticalCount;
        document.getElementById('temp-alerts').textContent = state.temperatureAlerts.length;
    } catch (error) {
        console.error('Error loading temperature alerts:', error);
    }
}

// Load Sensor Readings
async function loadSensorReadings() {
    try {
        // This would normally fetch sensor readings for specific shipments
        // For demo, we're using the alerts data
        state.sensorReadings = state.temperatureAlerts;
    } catch (error) {
        console.error('Error loading sensor readings:', error);
    }
}

// Load Critical Alerts
async function loadCriticalAlerts() {
    try {
        const response = await fetch(`${API_BASE_URL}/cold-chain/health/critical`);
        const alerts = await response.json();
        
        const container = document.getElementById('critical-temp-alerts');
        if (alerts.length === 0) {
            container.innerHTML = '<p class="text-center">✓ No critical temperature alerts</p>';
            return;
        }

        container.innerHTML = alerts.map(alert => `
            <div class="alert-item critical">
                <strong>⚠️ ${alert.shipment_id}</strong>
                <p><strong>Temperature:</strong> ${alert.temperature}°C (Range: ${alert.expected_range})</p>
                <p><strong>Severity:</strong> ${alert.severity.toUpperCase()}</p>
                <p><strong>Cargo Value:</strong> $${(alert.cargo_value || 0).toLocaleString()}</p>
                <p><small>${alert.regulatory_impact}</small></p>
            </div>
        `).join('');
    } catch (error) {
        console.error('Error loading critical alerts:', error);
    }
}

// Load Active Disruptions List
async function loadActiveDisruptionsList() {
    try {
        const response = await fetch(`${API_BASE_URL}/disruptions/?is_active=true`);
        const disruptions = await response.json();
        
        const container = document.getElementById('active-disruptions-list');
        if (disruptions.length === 0) {
            container.innerHTML = '<p class="text-center">✓ No active disruptions</p>';
            return;
        }

        container.innerHTML = disruptions.map(d => `
            <div class="alert-item ${d.severity === 'critical' ? 'critical' : ''}">
                <strong>🚨 ${d.title}</strong>
                <p><strong>Region:</strong> ${d.affected_region} | <strong>Severity:</strong> ${d.severity.toUpperCase()}</p>
                <p><strong>Type:</strong> ${d.disruption_type} | <strong>Affected Shipments:</strong> ${d.affected_shipments_count}</p>
                <p><small>${d.description}</small></p>
            </div>
        `).join('');
    } catch (error) {
        console.error('Error loading disruptions:', error);
    }
}

// Display Shipments
function displayShipments() {
    const tbody = document.getElementById('shipments-tbody');
    
    if (state.shipments.length === 0) {
        tbody.innerHTML = '<tr><td colspan="10" class="text-center">No shipments found</td></tr>';
        return;
    }

    tbody.innerHTML = state.shipments.map(shipment => `
        <tr>
            <td><strong>${shipment.shipment_id}</strong></td>
            <td>${shipment.origin}</td>
            <td>${shipment.destination}</td>
            <td>${shipment.cargo_description}</td>
            <td>$${shipment.cargo_value.toLocaleString()}</td>
            <td><span class="status-badge ${shipment.status}">${shipment.status.replace('_', ' ').toUpperCase()}</span></td>
            <td>${shipment.current_location || '-'}</td>
            <td>${formatDate(shipment.estimated_delivery)}</td>
            <td>${shipment.is_cold_chain ? '🧊 Cold Chain' : 'Standard'}</td>
            <td>
                <button class="action-btn btn-secondary" onclick="viewShipmentDetails('${shipment.shipment_id}')">View</button>
            </td>
        </tr>
    `).join('');
}

// Display Disruptions
function displayDisruptions() {
    const container = document.getElementById('disruptions-list');
    
    if (state.disruptions.length === 0) {
        container.innerHTML = '<p class="text-center">No disruptions</p>';
        return;
    }

    container.innerHTML = state.disruptions.map(d => `
        <div class="list-item ${d.severity === 'critical' ? 'critical' : d.severity === 'high' ? 'warning' : ''}">
            <div class="list-item-header">
                <div class="list-item-title">${d.title}</div>
                <span class="status-badge ${d.is_active ? 'in_transit' : 'delivered'}">
                    ${d.is_active ? 'ACTIVE' : 'RESOLVED'}
                </span>
            </div>
            <p>${d.description}</p>
            <div class="list-item-meta">
                <span><strong>Region:</strong> ${d.affected_region}</span>
                <span><strong>Type:</strong> ${d.disruption_type}</span>
                <span><strong>Severity:</strong> ${d.severity.toUpperCase()}</span>
                <span><strong>Affected:</strong> ${d.affected_shipments_count} shipments</span>
            </div>
        </div>
    `).join('');
}

// Display Fleet
function displayFleet() {
    const tbody = document.getElementById('fleet-tbody');
    
    if (state.fleetAssets.length === 0) {
        tbody.innerHTML = '<tr><td colspan="9" class="text-center">No fleet assets</td></tr>';
        return;
    }

    tbody.innerHTML = state.fleetAssets.map(asset => `
        <tr>
            <td><strong>${asset.asset_id}</strong></td>
            <td>${asset.asset_type.toUpperCase()}</td>
            <td><span class="status-badge ${asset.status}">${asset.status.replace('_', ' ').toUpperCase()}</span></td>
            <td>${asset.current_location || '-'}</td>
            <td>${asset.capacity_tons}</td>
            <td>${asset.is_cold_chain_capable ? '✓ Yes' : 'No'}</td>
            <td>${asset.current_shipment || 'None'}</td>
            <td>${formatDate(asset.available_from)}</td>
            <td>
                ${asset.status === 'idle' ? `<button class="action-btn btn-success" onclick="deployAsset('${asset.asset_id}')">Deploy</button>` : `<button class="action-btn btn-secondary" onclick="returnAsset('${asset.asset_id}')">Return</button>`}
            </td>
        </tr>
    `).join('');
}

// Display Cold Chain Alerts
function displayColdChainAlerts() {
    const container = document.getElementById('temp-alerts-list');
    
    if (state.temperatureAlerts.length === 0) {
        container.innerHTML = '<p class="text-center">No temperature alerts</p>';
        return;
    }

    container.innerHTML = state.temperatureAlerts.map(alert => `
        <div class="temp-alert-card ${alert.severity === 'critical' ? 'critical' : ''}">
            <div class="temp-alert-content">
                <strong>${alert.shipment_id}</strong>
                <p>Temperature: ${alert.temperature_recorded}°C (Expected: ${alert.expected_min}-${alert.expected_max}°C)</p>
                <p>Duration: ${alert.duration_minutes} minutes | Severity: <strong>${alert.severity.toUpperCase()}</strong></p>
                <small>${alert.regulatory_impact}</small>
            </div>
            <button class="action-btn ${alert.acknowledged ? 'btn-secondary' : 'btn-danger'}" 
                onclick="acknowledgeAlert('${alert.alert_id}')">
                ${alert.acknowledged ? 'Acknowledged' : 'Acknowledge'}
            </button>
        </div>
    `).join('');
}

// Display Sensor Readings
function displaySensorReadings() {
    const tbody = document.getElementById('sensors-tbody');
    
    if (state.temperatureAlerts.length === 0) {
        tbody.innerHTML = '<tr><td colspan="6" class="text-center">No sensor readings</td></tr>';
        return;
    }

    tbody.innerHTML = state.temperatureAlerts.slice(0, 20).map(reading => `
        <tr>
            <td>${reading.sensor_id}</td>
            <td>${reading.shipment_id}</td>
            <td>${reading.temperature_recorded}°C</td>
            <td>-</td>
            <td>-</td>
            <td>${formatDate(reading.timestamp)}</td>
        </tr>
    `).join('');
}

// Filter Functions
function filterShipments() {
    const status = document.getElementById('status-filter').value;
    const coldChainOnly = document.getElementById('cold-chain-filter').checked;
    const search = document.getElementById('shipment-search').value.toLowerCase();

    const filtered = state.shipments.filter(s => 
        (!status || s.status === status) &&
        (!coldChainOnly || s.is_cold_chain) &&
        (s.shipment_id.toLowerCase().includes(search) || 
         s.cargo_description.toLowerCase().includes(search))
    );

    // Update table with filtered data
    const tbody = document.getElementById('shipments-tbody');
    tbody.innerHTML = filtered.map(shipment => `
        <tr>
            <td><strong>${shipment.shipment_id}</strong></td>
            <td>${shipment.origin}</td>
            <td>${shipment.destination}</td>
            <td>${shipment.cargo_description}</td>
            <td>$${shipment.cargo_value.toLocaleString()}</td>
            <td><span class="status-badge ${shipment.status}">${shipment.status.replace('_', ' ').toUpperCase()}</span></td>
            <td>${shipment.current_location || '-'}</td>
            <td>${formatDate(shipment.estimated_delivery)}</td>
            <td>${shipment.is_cold_chain ? '🧊 Cold Chain' : 'Standard'}</td>
            <td>
                <button class="action-btn btn-secondary" onclick="viewShipmentDetails('${shipment.shipment_id}')">View</button>
            </td>
        </tr>
    `).join('');
}

function filterDisruptions() {
    const severity = document.getElementById('disruption-severity').value;
    const activeOnly = document.getElementById('active-only').checked;

    const filtered = state.disruptions.filter(d => 
        (!severity || d.severity === severity) &&
        (!activeOnly || d.is_active)
    );

    const container = document.getElementById('disruptions-list');
    container.innerHTML = filtered.map(d => `
        <div class="list-item ${d.severity === 'critical' ? 'critical' : d.severity === 'high' ? 'warning' : ''}">
            <div class="list-item-header">
                <div class="list-item-title">${d.title}</div>
                <span class="status-badge ${d.is_active ? 'in_transit' : 'delivered'}">
                    ${d.is_active ? 'ACTIVE' : 'RESOLVED'}
                </span>
            </div>
            <p>${d.description}</p>
            <div class="list-item-meta">
                <span><strong>Region:</strong> ${d.affected_region}</span>
                <span><strong>Type:</strong> ${d.disruption_type}</span>
                <span><strong>Severity:</strong> ${d.severity.toUpperCase()}</span>
                <span><strong>Affected:</strong> ${d.affected_shipments_count} shipments</span>
            </div>
        </div>
    `).join('');
}

function filterFleet() {
    const type = document.getElementById('asset-type-filter').value;
    const status = document.getElementById('asset-status-filter').value;
    const coldChainOnly = document.getElementById('cold-chain-asset-filter').checked;

    const filtered = state.fleetAssets.filter(a => 
        (!type || a.asset_type === type) &&
        (!status || a.status === status) &&
        (!coldChainOnly || a.is_cold_chain_capable)
    );

    const tbody = document.getElementById('fleet-tbody');
    tbody.innerHTML = filtered.map(asset => `
        <tr>
            <td><strong>${asset.asset_id}</strong></td>
            <td>${asset.asset_type.toUpperCase()}</td>
            <td><span class="status-badge ${asset.status}">${asset.status.replace('_', ' ').toUpperCase()}</span></td>
            <td>${asset.current_location || '-'}</td>
            <td>${asset.capacity_tons}</td>
            <td>${asset.is_cold_chain_capable ? '✓ Yes' : 'No'}</td>
            <td>${asset.current_shipment || 'None'}</td>
            <td>${formatDate(asset.available_from)}</td>
            <td>
                ${asset.status === 'idle' ? `<button class="action-btn btn-success" onclick="deployAsset('${asset.asset_id}')">Deploy</button>` : `<button class="action-btn btn-secondary" onclick="returnAsset('${asset.asset_id}')">Return</button>`}
            </td>
        </tr>
    `).join('');
}

function filterTemperatureAlerts() {
    const severity = document.getElementById('alert-severity-filter').value;
    const unacknowledgedOnly = document.getElementById('unacknowledged-only').checked;
    const search = document.getElementById('cold-shipment-search').value.toLowerCase();

    const filtered = state.temperatureAlerts.filter(a => 
        (!severity || a.severity === severity) &&
        (!unacknowledgedOnly || !a.acknowledged) &&
        (a.shipment_id.toLowerCase().includes(search))
    );

    const container = document.getElementById('temp-alerts-list');
    container.innerHTML = filtered.map(alert => `
        <div class="temp-alert-card ${alert.severity === 'critical' ? 'critical' : ''}">
            <div class="temp-alert-content">
                <strong>${alert.shipment_id}</strong>
                <p>Temperature: ${alert.temperature_recorded}°C (Expected: ${alert.expected_min}-${alert.expected_max}°C)</p>
                <p>Duration: ${alert.duration_minutes} minutes | Severity: <strong>${alert.severity.toUpperCase()}</strong></p>
                <small>${alert.regulatory_impact}</small>
            </div>
            <button class="action-btn ${alert.acknowledged ? 'btn-secondary' : 'btn-danger'}" 
                onclick="acknowledgeAlert('${alert.alert_id}')">
                ${alert.acknowledged ? 'Acknowledged' : 'Acknowledge'}
            </button>
        </div>
    `).join('');
}

// Action Functions
async function viewShipmentDetails(shipmentId) {
    alert(`Viewing details for shipment: ${shipmentId}\n\n(In a full implementation, this would show a modal with detailed information)`);
}

async function deployAsset(assetId) {
    const shipmentId = prompt('Enter shipment ID to assign to this asset:');
    if (!shipmentId) return;

    try {
        const response = await fetch(`${API_BASE_URL}/fleet/${assetId}/deploy`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ shipment_id: shipmentId })
        });

        if (response.ok) {
            alert(`Asset ${assetId} deployed to shipment ${shipmentId}`);
            refreshData();
        }
    } catch (error) {
        alert('Error deploying asset: ' + error.message);
    }
}

async function returnAsset(assetId) {
    try {
        const response = await fetch(`${API_BASE_URL}/fleet/${assetId}/return`, {
            method: 'POST'
        });

        if (response.ok) {
            alert(`Asset ${assetId} returned to idle`);
            refreshData();
        }
    } catch (error) {
        alert('Error returning asset: ' + error.message);
    }
}

async function acknowledgeAlert(alertId) {
    try {
        const response = await fetch(`${API_BASE_URL}/cold-chain/alerts/${alertId}/acknowledge`, {
            method: 'PATCH'
        });

        if (response.ok) {
            alert('Alert acknowledged');
            refreshData();
        }
    } catch (error) {
        alert('Error acknowledging alert: ' + error.message);
    }
}

// Utility Functions
function formatDate(dateStr) {
    if (!dateStr) return '-';
    const date = new Date(dateStr);
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
}

function updateAPIStatus(isOnline) {
    const indicator = document.getElementById('api-status');
    if (isOnline) {
        indicator.classList.remove('offline');
        indicator.classList.add('online');
        indicator.textContent = '● API Connected';
    } else {
        indicator.classList.remove('online');
        indicator.classList.add('offline');
        indicator.textContent = '● API Offline';
    }
}
