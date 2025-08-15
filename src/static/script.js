// Variáveis globais
let currentResults = [];
let isLoading = false;

// Elementos DOM
const searchForm = document.getElementById('searchForm');
const searchBtn = document.getElementById('searchBtn');
const loadingSection = document.getElementById('loadingSection');
const resultsSection = document.getElementById('resultsSection');
const resultsStats = document.getElementById('resultsStats');
const resultsList = document.getElementById('resultsList');
const exportBtn = document.getElementById('exportBtn');
const newSearchBtn = document.getElementById('newSearchBtn');
const exportModal = document.getElementById('exportModal');
const modalClose = document.getElementById('modalClose');
const progressFill = document.getElementById('progressFill');

// Event Listeners
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

function initializeApp() {
    // Event listeners para formulário
    searchForm.addEventListener('submit', handleSearch);
    
    // Event listeners para botões
    exportBtn.addEventListener('click', handleExport);
    newSearchBtn.addEventListener('click', handleNewSearch);
    modalClose.addEventListener('click', closeModal);
    
    // Fechar modal clicando fora
    exportModal.addEventListener('click', function(e) {
        if (e.target === exportModal) {
            closeModal();
        }
    });
    
    // Verificar saúde do serviço
    checkServiceHealth();
}

async function checkServiceHealth() {
    try {
        const response = await fetch('/api/health');
        const data = await response.json();
        console.log('Service health:', data);
    } catch (error) {
        console.error('Service health check failed:', error);
        showNotification('Erro ao conectar com o serviço', 'error');
    }
}

async function handleSearch(e) {
    e.preventDefault();
    
    if (isLoading) return;
    
    const searchQuery = document.getElementById('searchQuery').value.trim();
    const maxResults = parseInt(document.getElementById('maxResults').value);
    
    if (!searchQuery) {
        showNotification('Por favor, digite um termo de pesquisa', 'warning');
        return;
    }
    
    await performSearch(searchQuery, maxResults);
}

async function performSearch(searchQuery, maxResults) {
    try {
        isLoading = true;
        showLoading();
        
        const response = await fetch('/api/scrape', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                search_query: searchQuery,
                max_results: maxResults
            })
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        
        if (data.success) {
            currentResults = data.results;
            displayResults(data.results, data.total_results);
            showNotification(`${data.total_results} empresas encontradas!`, 'success');
        } else {
            throw new Error(data.error || 'Erro desconhecido');
        }
        
    } catch (error) {
        console.error('Erro durante scraping:', error);
        showNotification(`Erro durante a busca: ${error.message}`, 'error');
        hideLoading();
    } finally {
        isLoading = false;
    }
}

function showLoading() {
    loadingSection.style.display = 'block';
    resultsSection.style.display = 'none';
    searchBtn.disabled = true;
    searchBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Processando...';
    
    // Simular progresso
    let progress = 0;
    const progressInterval = setInterval(() => {
        progress += Math.random() * 15;
        if (progress > 90) progress = 90;
        progressFill.style.width = progress + '%';
    }, 500);
    
    // Limpar intervalo quando necessário
    setTimeout(() => {
        clearInterval(progressInterval);
    }, 30000);
}

function hideLoading() {
    loadingSection.style.display = 'none';
    searchBtn.disabled = false;
    searchBtn.innerHTML = '<i class="fas fa-search"></i> Iniciar Scraping';
    progressFill.style.width = '0%';
}

function displayResults(results, totalResults) {
    hideLoading();
    
    // Mostrar seção de resultados
    resultsSection.style.display = 'block';
    resultsSection.scrollIntoView({ behavior: 'smooth' });
    
    // Exibir estatísticas
    displayStats(results, totalResults);
    
    // Exibir grid de resultados
    displayResultsList(results);
}

function displayStats(results, totalResults) {
    const withPhone = results.filter(r => r.phone && r.phone !== 'N/A').length;
    const withWebsite = results.filter(r => r.website && r.website !== 'N/A').length;
    const withEmail = results.filter(r => r.emails && r.emails.length > 0).length;
    const withSocial = results.filter(r => r.social_media && Object.keys(r.social_media).length > 0).length;
    
    resultsStats.innerHTML = `
        <div class="stats-grid" style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem;">
            <div class="stat-item" style="text-align: center; padding: 1rem; background: #f8f9fa; border-radius: 10px;">
                <div style="font-size: 2rem; font-weight: bold; color: #4CAF50;">${totalResults}</div>
                <div style="color: #666;">Total de Empresas</div>
            </div>
            <div class="stat-item" style="text-align: center; padding: 1rem; background: #f8f9fa; border-radius: 10px;">
                <div style="font-size: 2rem; font-weight: bold; color: #2196F3;">${withPhone}</div>
                <div style="color: #666;">Com Telefone</div>
            </div>
            <div class="stat-item" style="text-align: center; padding: 1rem; background: #f8f9fa; border-radius: 10px;">
                <div style="font-size: 2rem; font-weight: bold; color: #FF9800;">${withWebsite}</div>
                <div style="color: #666;">Com Website</div>
            </div>
            <div class="stat-item" style="text-align: center; padding: 1rem; background: #f8f9fa; border-radius: 10px;">
                <div style="font-size: 2rem; font-weight: bold; color: #9C27B0;">${withEmail}</div>
                <div style="color: #666;">Com Email</div>
            </div>
            <div class="stat-item" style="text-align: center; padding: 1rem; background: #f8f9fa; border-radius: 10px;">
                <div style="font-size: 2rem; font-weight: bold; color: #E91E63;">${withSocial}</div>
                <div style="color: #666;">Com Redes Sociais</div>
            </div>
        </div>
    `;
}

function displayResultsList(results) {
    if (results.length === 0) {
        resultsList.innerHTML = `
            <div class="empty-results">
                <i class="fas fa-search"></i>
                <h3>Nenhum resultado encontrado</h3>
                <p>Tente ajustar os termos de pesquisa.</p>
            </div>
        `;
        return;
    }
    
    // Criar tabela
    let tableHTML = `
        <table class="results-table">
            <thead>
                <tr>
                    <th class="col-name">Empresa</th>
                    <th class="col-address">Endereço</th>
                    <th class="col-contact">Contato</th>
                    <th class="col-website">Website</th>
                    <th class="col-rating">Avaliação</th>
                    <th class="col-actions">Ações</th>
                </tr>
            </thead>
            <tbody>
    `;
    
    results.forEach((result, index) => {
        const emails = result.emails && result.emails.length > 0 ? result.emails.slice(0, 2).join(', ') : '';
        const phones = result.phones && result.phones.length > 0 ? result.phones.slice(0, 2).join(', ') : result.phone || '';
        const socialMedia = result.social_media || {};
        
        // Criar links de redes sociais
        const socialLinks = Object.entries(socialMedia).map(([platform, url]) => 
            `<a href="https://${url}" target="_blank" title="${platform}" class="fa fa-${platform}"></a>`
        ).join('');
        
        // Criar informações de contato
        let contactInfo = '';
        if (phones && phones !== 'N/A') {
            contactInfo += `<div class="contact-item"><i class="fas fa-phone"></i> ${phones}</div>`;
        }
        if (emails) {
            contactInfo += `<div class="contact-item"><i class="fas fa-envelope"></i> ${emails}</div>`;
        }
        if (socialLinks) {
            contactInfo += `<div class="contact-item"><i class="fas fa-share-alt"></i> <div class="social-links">${socialLinks}</div></div>`;
        }
        if (!contactInfo) {
            contactInfo = '<span style="color: #999;">Não disponível</span>';
        }
        
        // Criar rating com estrelas
        let ratingHTML = '';
        if (result.rating && result.rating !== 'N/A') {
            const rating = parseFloat(result.rating);
            if (!isNaN(rating)) {
                const stars = Math.round(rating);
                ratingHTML = `
                    <div class="rating">
                        ${Array(5).fill().map((_, i) => 
                            `<i class="fas fa-star" style="color: ${i < stars ? '#FFD700' : '#ddd'}"></i>`
                        ).join('')}
                        <span>${rating}</span>
                    </div>
                `;
            } else {
                ratingHTML = result.rating;
            }
        } else {
            ratingHTML = '<span style="color: #999;">N/A</span>';
        }
        
        tableHTML += `
            <tr>
                <td class="col-name" data-label="Empresa">
                    <strong>${result.name || 'Nome não disponível'}</strong>
                </td>
                <td class="col-address" data-label="Endereço">
                    ${result.address || 'Endereço não disponível'}
                </td>
                <td class="col-contact" data-label="Contato">
                    <div class="contact-info">${contactInfo}</div>
                </td>
                <td class="col-website" data-label="Website">
                    ${result.website && result.website !== 'N/A' 
                        ? `<a href="${result.website}" target="_blank" class="btn-small btn-website">Visitar</a>`
                        : '<span style="color: #999;">N/A</span>'
                    }
                </td>
                <td class="col-rating" data-label="Avaliação">
                    ${ratingHTML}
                </td>
                <td class="col-actions" data-label="Ações">
                    ${result.google_maps_url 
                        ? `<a href="${result.google_maps_url}" target="_blank" class="btn-small btn-maps">Maps</a>`
                        : '<span style="color: #999;">N/A</span>'
                    }
                </td>
            </tr>
        `;
    });
    
    tableHTML += `
            </tbody>
        </table>
    `;
    
    resultsList.innerHTML = tableHTML;
}

async function handleExport() {
    if (currentResults.length === 0) {
        showNotification('Nenhum resultado para exportar', 'warning');
        return;
    }
    
    try {
        showModal();
        
        const response = await fetch('/api/export', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                results: currentResults
            })
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        
        if (data.success) {
            // Criar link de download
            const downloadLink = document.createElement('a');
            downloadLink.href = data.download_url;
            downloadLink.download = data.filename;
            downloadLink.click();
            
            showNotification('Arquivo CSV exportado com sucesso!', 'success');
        } else {
            throw new Error(data.error || 'Erro na exportação');
        }
        
    } catch (error) {
        console.error('Erro durante exportação:', error);
        showNotification(`Erro na exportação: ${error.message}`, 'error');
    } finally {
        closeModal();
    }
}

function handleNewSearch() {
    // Limpar resultados
    currentResults = [];
    resultsSection.style.display = 'none';
    
    // Limpar formulário
    document.getElementById('searchQuery').value = '';
    document.getElementById('maxResults').value = '50';
    
    // Scroll para o topo
    window.scrollTo({ top: 0, behavior: 'smooth' });
    
    // Focar no campo de pesquisa
    document.getElementById('searchQuery').focus();
}

function showModal() {
    exportModal.style.display = 'flex';
    document.body.style.overflow = 'hidden';
}

function closeModal() {
    exportModal.style.display = 'none';
    document.body.style.overflow = 'auto';
}

function showNotification(message, type = 'info') {
    // Remover notificações existentes
    const existingNotifications = document.querySelectorAll('.notification');
    existingNotifications.forEach(n => n.remove());
    
    // Criar nova notificação
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: ${getNotificationColor(type)};
        color: white;
        padding: 1rem 1.5rem;
        border-radius: 10px;
        box-shadow: 0 5px 15px rgba(0,0,0,0.2);
        z-index: 10000;
        max-width: 400px;
        animation: slideIn 0.3s ease-out;
    `;
    
    notification.innerHTML = `
        <div style="display: flex; align-items: center; gap: 0.5rem;">
            <i class="fas ${getNotificationIcon(type)}"></i>
            <span>${message}</span>
            <button onclick="this.parentElement.parentElement.remove()" 
                    style="background: none; border: none; color: white; margin-left: auto; cursor: pointer; font-size: 1.2rem;">
                &times;
            </button>
        </div>
    `;
    
    document.body.appendChild(notification);
    
    // Auto-remover após 5 segundos
    setTimeout(() => {
        if (notification.parentElement) {
            notification.remove();
        }
    }, 5000);
}

function getNotificationColor(type) {
    const colors = {
        success: '#4CAF50',
        error: '#f44336',
        warning: '#FF9800',
        info: '#2196F3'
    };
    return colors[type] || colors.info;
}

function getNotificationIcon(type) {
    const icons = {
        success: 'fa-check-circle',
        error: 'fa-exclamation-circle',
        warning: 'fa-exclamation-triangle',
        info: 'fa-info-circle'
    };
    return icons[type] || icons.info;
}

// Adicionar estilos para animação de notificação
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from {
            transform: translateX(100%);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
`;
document.head.appendChild(style);

