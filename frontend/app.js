// Inventory Management Frontend Application
class InventoryApp {
    constructor() {
        this.apiBaseUrl = window.location.protocol === 'file:' 
            ? 'http://localhost:8000/api' 
            : (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
                ? `${window.location.protocol}//${window.location.hostname}:8000/api`
                : `/api`);
        
        this.wsUrl = window.location.protocol === 'https:' 
            ? `wss://${window.location.hostname}:8001/`
            : (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
                ? `ws://${window.location.hostname}:8001/`
                : `ws://${window.location.host.split(':')[0]}:8001/`);
        
        this.socket = null;
        this.items = [];
        this.editModal = null;
        
        this.init();
    }

    init() {
        // Initialize Bootstrap modal
        this.editModal = new bootstrap.Modal(document.getElementById('editModal'));
        
        // Setup event listeners
        this.setupEventListeners();
        
        // Connect to WebSocket
        this.connectWebSocket();
        
        // Load initial data
        this.loadItems();
    }

    setupEventListeners() {
        // Add item form
        document.getElementById('addItemForm').addEventListener('submit', (e) => {
            e.preventDefault();
            this.addItem();
        });

        // Edit item form
        document.getElementById('saveEditBtn').addEventListener('click', () => {
            this.saveEditItem();
        });

        // Refresh button
        document.getElementById('refreshBtn').addEventListener('click', () => {
            this.loadItems();
        });
    }

    connectWebSocket() {
        try {
            this.socket = new WebSocket(this.wsUrl);
            
            this.socket.onopen = () => {
                console.log('WebSocket connected');
                this.updateWebSocketStatus(true);
            };

            this.socket.onmessage = (event) => {
                const data = JSON.parse(event.data);
                this.handleWebSocketMessage(data);
            };

            this.socket.onclose = () => {
                console.log('WebSocket disconnected');
                this.updateWebSocketStatus(false);
                
                // Attempt to reconnect after 3 seconds
                setTimeout(() => {
                    this.connectWebSocket();
                }, 3000);
            };

            this.socket.onerror = (error) => {
                console.error('WebSocket error:', error);
                this.updateWebSocketStatus(false);
            };
        } catch (error) {
            console.error('Failed to connect WebSocket:', error);
            this.updateWebSocketStatus(false);
        }
    }

    updateWebSocketStatus(connected) {
        const statusEl = document.getElementById('websocketStatus');
        if (connected) {
            statusEl.className = 'websocket-status websocket-connected';
            statusEl.innerHTML = '<i class="fas fa-circle"></i> WebSocket: Connected';
        } else {
            statusEl.className = 'websocket-status websocket-disconnected';
            statusEl.innerHTML = '<i class="fas fa-circle"></i> WebSocket: Disconnected';
        }
    }

    handleWebSocketMessage(data) {
        console.log('WebSocket message:', data);
        
        switch (data.type) {
            case 'connection_established':
                this.showNotification('Connected to real-time updates', 'success');
                break;
                
            case 'item_created':
                this.showNotification(`New item created: ${data.data.name}`, 'success');
                this.loadItems(); // Refresh the list
                break;
                
            case 'item_updated':
                this.showNotification(`Item updated: ${data.data.name}`, 'info');
                this.loadItems(); // Refresh the list
                break;
                
            case 'item_deleted':
                this.showNotification(data.data.message, 'warning');
                this.loadItems(); // Refresh the list
                break;
                
            default:
                console.log('Unknown message type:', data.type);
        }
    }

    async loadItems() {
        try {
            this.showLoading(true);
            const response = await fetch(`${this.apiBaseUrl}/items/`);
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            this.items = await response.json();
            this.renderItems();
            this.updateItemCount();
        } catch (error) {
            console.error('Error loading items:', error);
            this.showNotification('Error loading items. Please try again.', 'danger');
        } finally {
            this.showLoading(false);
        }
    }

    async addItem() {
        const formData = this.getFormData('addItemForm');
        
        try {
            const response = await fetch(`${this.apiBaseUrl}/items/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(formData)
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || 'Failed to create item');
            }

            const newItem = await response.json();
            this.showNotification(`Item "${newItem.name}" created successfully!`, 'success');
            
            // Reset form
            document.getElementById('addItemForm').reset();
            
            // Reload items (WebSocket should also trigger this)
            this.loadItems();
            
        } catch (error) {
            console.error('Error adding item:', error);
            this.showNotification(`Error: ${error.message}`, 'danger');
        }
    }

    async editItem(itemId) {
        const item = this.items.find(i => i.id === itemId);
        if (!item) return;

        // Populate edit form
        document.getElementById('editItemId').value = item.id;
        document.getElementById('editItemName').value = item.name;
        document.getElementById('editItemCategory').value = item.category;
        document.getElementById('editItemPrice').value = item.price;
        document.getElementById('editItemQuantity').value = item.quantity;
        document.getElementById('editItemDescription').value = item.description || '';

        this.editModal.show();
    }

    async saveEditItem() {
        const itemId = document.getElementById('editItemId').value;
        const formData = this.getFormData('editItemForm');
        
        try {
            const response = await fetch(`${this.apiBaseUrl}/items/${itemId}/`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(formData)
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || 'Failed to update item');
            }

            const updatedItem = await response.json();
            this.showNotification(`Item "${updatedItem.name}" updated successfully!`, 'success');
            
            this.editModal.hide();
            this.loadItems();
            
        } catch (error) {
            console.error('Error updating item:', error);
            this.showNotification(`Error: ${error.message}`, 'danger');
        }
    }

    async deleteItem(itemId, itemName) {
        if (!confirm(`Are you sure you want to delete "${itemName}"?`)) {
            return;
        }

        try {
            const response = await fetch(`${this.apiBaseUrl}/items/${itemId}/`, {
                method: 'DELETE'
            });

            if (!response.ok) {
                throw new Error('Failed to delete item');
            }

            this.showNotification(`Item "${itemName}" deleted successfully!`, 'success');
            this.loadItems();
            
        } catch (error) {
            console.error('Error deleting item:', error);
            this.showNotification(`Error: ${error.message}`, 'danger');
        }
    }

    getFormData(formId) {
        const form = document.getElementById(formId);
        const formData = new FormData(form);
        const data = {};
        
        // Get form data based on form type
        if (formId === 'addItemForm') {
            data.name = document.getElementById('itemName').value;
            data.category = document.getElementById('itemCategory').value;
            data.price = parseFloat(document.getElementById('itemPrice').value);
            data.quantity = parseInt(document.getElementById('itemQuantity').value) || 0;
            data.description = document.getElementById('itemDescription').value;
        } else if (formId === 'editItemForm') {
            data.name = document.getElementById('editItemName').value;
            data.category = document.getElementById('editItemCategory').value;
            data.price = parseFloat(document.getElementById('editItemPrice').value);
            data.quantity = parseInt(document.getElementById('editItemQuantity').value) || 0;
            data.description = document.getElementById('editItemDescription').value;
        }
        
        return data;
    }

    renderItems() {
        const container = document.getElementById('itemsGrid');
        const noItemsEl = document.getElementById('noItems');
        
        if (this.items.length === 0) {
            container.innerHTML = '';
            noItemsEl.style.display = 'block';
            return;
        }
        
        noItemsEl.style.display = 'none';
        
        container.innerHTML = this.items.map(item => `
            <div class="col-md-6 col-lg-4 mb-4">
                <div class="card item-card h-100">
                    <div class="card-body">
                        <div class="d-flex justify-content-between align-items-start mb-2">
                            <h5 class="card-title mb-0">${this.escapeHtml(item.name)}</h5>
                            <span class="badge bg-primary price-badge">$${item.price}</span>
                        </div>
                        
                        <div class="mb-2">
                            <span class="badge bg-secondary category-badge">${this.escapeHtml(item.category)}</span>
                            <span class="badge bg-${item.quantity > 0 ? 'success' : 'warning'} quantity-badge ms-1">
                                Qty: ${item.quantity}
                            </span>
                        </div>
                        
                        ${item.description ? `
                            <p class="card-text text-muted small">${this.escapeHtml(item.description)}</p>
                        ` : ''}
                        
                        <div class="d-flex justify-content-between align-items-center mt-3">
                            <small class="text-muted">
                                Created: ${this.formatDate(item.created_at)}
                            </small>
                            <div class="btn-group" role="group">
                                <button class="btn btn-outline-primary btn-sm" onclick="app.editItem('${item.id}')">
                                    <i class="fas fa-edit"></i>
                                </button>
                                <button class="btn btn-outline-danger btn-sm" onclick="app.deleteItem('${item.id}', '${this.escapeHtml(item.name)}')">
                                    <i class="fas fa-trash"></i>
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `).join('');
    }

    updateItemCount() {
        document.getElementById('itemCount').textContent = `Items: ${this.items.length}`;
    }

    showLoading(show) {
        const spinner = document.getElementById('loadingSpinner');
        const grid = document.getElementById('itemsGrid');
        
        if (show) {
            spinner.style.display = 'block';
            grid.style.display = 'none';
        } else {
            spinner.style.display = 'none';
            grid.style.display = 'block';
        }
    }

    showNotification(message, type = 'info') {
        const container = document.getElementById('notifications');
        const id = 'notification-' + Date.now();
        
        const notification = document.createElement('div');
        notification.id = id;
        notification.className = `alert alert-${type} alert-dismissible fade show notification`;
        notification.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        container.appendChild(notification);
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            const el = document.getElementById(id);
            if (el) {
                const alert = new bootstrap.Alert(el);
                alert.close();
            }
        }, 5000);
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    formatDate(dateString) {
        if (!dateString) return 'N/A';
        const date = new Date(dateString);
        return date.toLocaleDateString() + ' ' + date.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
    }
}

// Initialize the application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.app = new InventoryApp();
});
