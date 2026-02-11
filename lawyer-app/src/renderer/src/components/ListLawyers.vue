<template>
    <div class="message">
        <p class="error" v-if="error != ''">{{error }}</p>
        <p class="success" v-if="success != ''">{{success }}</p>
    </div>
    <div class="list-lawyers">
        <div class="header">
            <h2>📋 Liste des avocats</h2>
            <button class="floating-add" @click="openAddModal">➕ Ajouter</button>
        </div>
        <div class="search-container">
            <div class="search-box">
                <span class="search-icon">🔍</span>
                <input v-model="options.search" type="text" class="search-input" placeholder="Rechercher par nom..." @input="filterLawyers" />
                <button v-if="options.search" class="clear-btn" @click="clearSearch">✕</button>
            </div>
            <div class="search-stats" v-if="options.search">{{lawyers.docs.length}} résultat(s) trouvé(s)
            </div>
        </div>
        <p v-if="loading == true" class="loading">⏳ Chargement en cours...</p>
        <div v-else class="table-container">
            <table class="lawyers-table">
                <thead>
                    <tr>
                        <th class="name-head-cell">Nom</th>
                        <th class="service-head-cell">Prestation de serment</th>
                        <th class="address-head-cell">Adresse</th>
                        <th class="actions-head-cell">Actions</th>
                    </tr>
                </thead>
                <tbody>
                    <tr v-for="lawyer in lawyers.docs" :key="lawyer._id" class="lawyer-row" @click="goToLawyer(lawyer._id,$event)">
                        <td class="name-cell">{{lawyer.title}}</td>
                        <td class="service-cell">{{lawyer.service}}</td>
                        <td class="address-cell">{{lawyer.address}}</td>
                        <td class="actions-cell">
                            <button class="btn edit" @click="openEditModal(lawyer)">✏️</button>
                            <button class="btn delete" @click="confirmDelete(lawyer)">🗑️</button>
                        </td>
                    </tr>
                    <tr v-if="lawyers.docs.length == 0" class="empty-row">
                        <td colspan="4" class="empty">❌ Aucun avocat trouvé</td>
                    </tr>
                </tbody>
            </table>
        </div>
        <div class="pagination">
            <button class="btn pagination-btn" :disabled="options.page === 1" @click="goPage(options.page - 1)">← Préc</button>
            <button class="btn pagination-btn" :disabled="options.page === 1" @click="goPage(1)">1</button>
            <button v-for="p in getPaginationPages()" :key="p" :class="['page',{active:p === options.page}]" @click="goPage(p)">{{p}}</button>
            <button class="btn pagination-btn" :disabled="options.page === lawyers.totalPages" @click="goPage(lawyers.totalPages)">{{lawyers.totalPages}}</button>
            <button class="btn pagination-btn" :disabled="options.page === lawyers.totalPages" @click="goPage(options.page + 1)">Suiv →</button>
            <input type="number" class="page-input" :min="1" v-model="inputPages" @input="goPage(parseInt(inputPages) || 1)" :max="lawyers.totalPages || 1" />
        </div>
        <!-- Modal for Add / Edit -->
        <div v-if="showModal" class="modal-overlay" @click.self="closeModal">
            <div class="modal">
                <div class="modal-header">
                    <h3>{{editingLawyer ? '✏️ Modifier l\'avocat' :'➕ Ajouter un avocat'}}</h3>
                    <button class="close-btn" @click="closeModal">✕</button>
                </div>
                <form @submit.prevent="saveLawyer" class="modal-form">
                    <div class="form-group">
                        <label for="title">Nom *</label>
                        <p class="inputError" v-if="errorInput?.title">{{errorInput.title}}</p>
                        <input id="title" name="title" v-model="form.title" type="text" placeholder="Nom complet" />
                    </div>
                    <div class="form-group">
                        <label for="phone">Téléphone</label>
                        <input id="phone" name="phone" v-model="form.contact.phone" type="tel" placeholder="+33 1 23 45 67 89" />
                    </div>
                    <div class="form-group">
                        <label for="email">Email</label>
                        <input id="email" name="email" v-model="form.contact.email" type="email" placeholder="email@example.com" />
                    </div>
                    <div class="form-group">
                        <label for="fax">Fax</label>
                        <input name="fax" id="fax" v-model="form.contact.fax" type="tel" placeholder="+33 1 23 45 67 89" />
                    </div>
                    <div class="form-group">
                        <label for="site">Site web</label>
                        <input id="site" name="site" v-model="form.contact.site" type="url" placeholder="https://example.com" />
                    </div>
                    <div class="form-group">
                        <label for="service">Prestation de serment</label>
                        <p class="inputError" v-if="errorInput?.service">{{errorInput.service}}</p>
                        <input id="service" name="service" v-model="form.service" type="text" />
                    </div>
                    <div class="form-group">
                        <label for="address">Adresse *</label>
                        <p class="inputError" v-if="errorInput?.address">{{errorInput?.address}}</p>
                        <textarea id="address" name="address" v-model="form.address" placeholder="Adresse complète" rows="3"></textarea>
                    </div>
                    <div class="modal-actions">
                        <button type="button" @click.stop="closeModal" class="btn secondary" @click="closeModal">Annuler</button>
                        <button type="submit" class="btn primary">Enregistrer</button>
                    </div>
                </form>
            </div>
        </div>
    </div>
    <div v-if="showDeleteConfirm" class="modal-overlay" @click.self="cancelDelete">
        <div class="modal confirm-modal">
            <div class="modal-header">
                <h3>⚠️ Confirmer la suppression</h3>
            </div>
            <div class="modal-body">
                <p>Êtes-vous sûr de vouloir supprimer <strong>{{ lawyerToDelete?.title }}</strong> ?</p>
            </div>
            <div class="modal-actions">
                <button type="button" @click="cancelDelete" class="btn secondary">Annuler</button>
                <button type="button" @click="deleteLawyer" class="btn delete">Supprimer</button>
            </div>
        </div>
    </div>
</template>
<script setup>
import{ref,onMounted}from 'vue'
import{useRouter}from 'vue-router'
import * as v from 'valibot'
let timeoutSearch;
const showDeleteConfirm = ref(false);
const lawyerToDelete = ref(null);
const router = useRouter(),
    lawyers = ref({docs:[],totalPages:1}),
    loading = ref(true),
    errorInput = ref({}),
    error = ref(""),
    success = ref(""),
    inputPages = ref(1),
    showModal = ref(false),
    editingLawyer = ref(null),
    form = ref({
        title:'',
        contact:{phone:'',email:'',fax:'',site:''},
        address:'',
        service:''
    }),
    options = ref({
        search:'',
        page:1,
        limit:10
    }),
    lawyerSchema = v.object({
        title:v.pipe(v.string("Le nom doit être en format textuel"),v.minLength(1,'Le nom est obligatoire')),
        service:v.pipe(v.string("La prestation de serment doit être en format textuel"),v.minLength(1,'La prestation de serment est obligatoire')),
        address:v.pipe(v.string("L'adresse doit être en format textuel"),v.minLength(1,'L\'adresse est obligatoire')),
        contact:v.object({
            phone:v.optional(v.string("Le téléphone doit être en format textuel")),
            email:v.optional(v.string("L'email doit être en format textuel")),
            fax:v.optional(v.string("Le fax doit être en format textuel")),
            site:v.optional(v.string("Le site doit être en format textuel"))
        })
    })
onMounted(async () => await loadLawyers())
async function loadLawyers(){
    try{
        lawyers.value = await window.electronAPI.getLawyer(JSON.parse(JSON.stringify(options.value)))
        loading.value = false;
    }catch (err){
        console.error('Erreur lors du chargement:',err)
        loading.value = false
        success.value = ""
        error.value = "Erreur de chargement des avocats";
    }
}
async function goPage(newPage){
    const page = parseInt(newPage)
    if (page > lawyers.value.totalPages){
        options.value.page = lawyers.value.totalPages
        inputPages.value = options.value.page
    }else if (page < 1){
        options.value.page = 1
        inputPages.value = 1
    }else{
        options.value.page = page
        inputPages.value = page
    }
    await loadLawyers()
}
function getPaginationPages(){
    const totalPages = lawyers.value.totalPages || 1,
       currentPage = options.value.page,
        pages = [],
        maxPages = 5
    let start = Math.max(2,currentPage - Math.floor(maxPages / 2)),
        end = Math.min(totalPages - 1,start + maxPages - 1)
    if (end - start + 1 < maxPages) start = Math.max(1,end - maxPages + 1)
    for (let i = start; i <= end; i++) pages.push(i)
    return pages
}
function filterLawyers(){
    clearTimeout(timeoutSearch);
    timeoutSearch = setTimeout(async function (){
        try{
            lawyers.value = await window.electronAPI.getLawyer(JSON.parse(JSON.stringify(options.value)))
        }catch (err){
            console.error('Erreur lors de la recherche:',err)
            error.value = "Erreur lors de la recherche";
        }
    },500)
}
async function clearSearch(){
    options.value.page = 1
    inputPages.value = 1
    options.value.search = '';
    try{
        lawyers.value = await window.electronAPI.getLawyer(JSON.parse(JSON.stringify(options.value)))
    }catch (err){
        console.error('Erreur lors de la recherche:',err)
        error.value = "Erreur lors du chargement";
    }
}
function openAddModal(){
    errorInput.value ={};
    editingLawyer.value = null
    form.value ={
        title:'',
        contact:{phone:'',email:'',fax:'',site:''},
        address:'',
        service:''
    }
    showModal.value = true
}
function openEditModal(lawyer){
    editingLawyer.value = lawyer
    form.value = JSON.parse(JSON.stringify(lawyer))
    showModal.value = true
}
function closeModal(){
    showModal.value = false
}
async function saveLawyer(){
    error.value = "";
    success.value = "";
    // Validate form
    const validationResult = v.safeParse(lawyerSchema,form.value);
    errorInput.value ={};
    if (!validationResult.success){
        validationResult.issues.map(issue => errorInput.value[issue.path[0].key] = issue.message)
        return;
    }
    try{
        if (editingLawyer.value){
            await window.electronAPI.updateLawyer(editingLawyer.value._id,JSON.parse(JSON.stringify(form.value)));
            success.value = "Modification de l'avocat " + form.value.title + " à été effectué avec succès."
        }else{
            await window.electronAPI.createLawyer(JSON.parse(JSON.stringify(form.value)));
            success.value = "L'avocat " + form.value.title + " à été ajouté avec succès."
        }
        await loadLawyers()
        closeModal()
        form.value ={
            title:'',
            contact:{phone:'',email:'',fax:'',site:''},
            address:'',
            service:''
        }
        editingLawyer.value = null;
    }catch (error){
        error.value = "Erreur lors de la sauvegarde de l'avocat";
        console.error('Erreur lors de la sauvegarde:',error)
    }
}
function goToLawyer(lawyerId,event){
    event.stopPropagation();
    // Don't navigate if clicking on action buttons
    if (event.target.closest('.actions-cell')) return
    router.push(`/lawyer/${lawyerId}`)
}
function confirmDelete(lawyer){
    lawyerToDelete.value = lawyer;
    showDeleteConfirm.value = true;
}
function cancelDelete(){
    showDeleteConfirm.value = false;
    lawyerToDelete.value = null;
}
async function deleteLawyer(){
    error.value = "";
    success.value = "";
    try{
        await window.electronAPI.deleteLawyer(lawyerToDelete.value._id);
        success.value = "L'avocat " + lawyerToDelete.value.title + " a été supprimé avec succès";
        showDeleteConfirm.value = false;
        lawyerToDelete.value = null;
        await loadLawyers();
    }catch(err){
        console.error("Erreur lors de la suppression", err);
        error.value = "Erreur lors de la suppression de l'avocat";
    }
}
</script>
<style scoped>
*{box-sizing:border-box}
.message{
    position:fixed;
    bottom:0;
    z-index:1000;
    left:0;
    width:100%;
    color:white;
    font-weight:bold
}
.inputError{
    color:red;
    font-size:.8em
}
.message p{
    padding:.8em 2em;
    width:100%;
    opacity:0;
    animation-name:hiddenMessage;
    animation-duration:5s;
    animation-timing-function:ease;
    text-align:center
}
.message .error{background:#f44336}
.message .success{background:#42b983}
.list-lawyers{
    padding:20px;
    min-height:100vh
}
.confirm-modal{max-width:400px}
.modal-body{
    padding:1em;
    text-align:center
}
.header{
    display:flex;
    justify-content:space-between;
    align-items:center;
    margin-bottom:24px;
    flex-wrap:wrap;
    gap:16px
}
h2{
    margin:0;
    color:#1a1a1a;
    font-size:28px
}
/* Search Container */
.search-container{
    margin-bottom:24px;
    animation:slideUp .3s ease
}
.modal-body{color:black}
.search-box{
    display:flex;
    align-items:center;
    background:white;
    border-radius:8px;
    box-shadow:0 2px 8px rgba(0,0,0,.08);
    border:2px solid transparent;
    transition:all .2s ease
}
.search-box input{padding:12px 16px}
.search-box:focus-within{
    border-color:#42b983;
    box-shadow:0 4px 12px rgba(66,185,131,.15)
}
.search-icon{
    font-size:20px;
    margin-right:12px;
    color:#999
}
.search-input{
    flex:1;
    border:none;
    outline:none;
    font-size:14px;
    color:#333;
    font-family:inherit
}
.search-input::placeholder{color:#999}
.clear-btn{
    background:none;
    border:none;
    font-size:18px;
    cursor:pointer;
    color:#999;
    padding:0;
    margin-right:12px;
    transition:color .2s ease;
    display:flex;
    align-items:center;
    justify-content:center
}
.clear-btn:hover{color:#333}
.search-stats{
    margin-top:8px;
    font-size:12px;
    color:#999;
    padding-left:32px
}
.loading{
    text-align:center;
    padding:40px;
    color:#666;
    font-size:16px
}
@keyframes slideUp{
    from{
        opacity:0;
        transform:translateY(10px)
    }
    to{
        opacity:1;
        transform:translateY(0)
    }
}
@keyframes hiddenMessage{
    0%{opacity:0}
    20%{opacity:1}
    80%{opacity:1}
    100%{opacity:0}
}
.table-container{
    background:white;
    border-radius:12px;
    box-shadow:0 8px 24px rgba(0,0,0,.12);
    overflow:hidden;
    margin-bottom:24px;
    animation:slideUp .3s ease
}
.lawyers-table{
    width:100%;
    border-collapse:collapse
}
.lawyers-table th{
    background:linear-gradient(135deg,#42b983 0%,#35956f 100%);
    color:white;
    padding:14px 16px;
    text-align:left;
    font-weight:600;
    font-size:13px;
    text-transform:uppercase;
    letter-spacing:.5px
}
.lawyers-table tbody tr{
    border-bottom:1px solid #f0f0f0;
    transition:all .2s ease
}
.lawyers-table tbody tr:hover{background:#f9f9f9}
.lawyer-row{cursor:pointer}
.lawyer-row td{
    padding:14px 16px;
    color:#333;
    font-size:14px
}
.name-cell{
    font-weight:500;
    color:#1a1a1a
}
.service-cell{
    color:#666;
    white-space:nowrap
}
.address-cell{
    color:#666;
    max-width:250px;
    overflow:hidden;
    text-overflow:ellipsis;
    white-space:nowrap
}
.actions-cell{
    display:flex;
    gap:6px;
    flex-wrap:wrap
}
.empty-row td{
    text-align:center;
    padding:40px 16px;
    color:#999;
    font-size:14px
}
/* Pagination */
.pagination{
    display:flex;
    gap:8px;
    align-items:center;
    margin-bottom:24px;
    flex-wrap:wrap;
    background:white;
    padding:16px;
    border-radius:8px;
    box-shadow:0 2px 8px rgba(0,0,0,.08)
}
.pagination-btn{
    padding:8px 12px;
    background:white;
    border:1px solid #ddd;
    border-radius:4px;
    cursor:pointer;
    font-size:13px;
    transition:all .2s ease
}
.pagination-btn:hover:not(:disabled){
    background:#42b983;
    color:white;
    border-color:#42b983
}
.pagination-btn:disabled{
    opacity:.5;
    cursor:not-allowed
}
.page{
    padding:8px 10px;
    border-radius:4px;
    border:1px solid #ddd;
    cursor:pointer;
    font-size:13px;
    transition:all .2s ease
}
.page:hover{border-color:#42b983}
.page.active{
    background:#42b983;
    color:white;
    border-color:#42b983
}
.page-input{
    width:60px;
    padding:8px;
    border:1px solid #ddd;
    border-radius:4px;
    font-size:13px
}
/* Buttons */
.btn{
    padding:8px 12px;
    border:1px solid #ddd;
    background:white;
    cursor:pointer;
    font-size:12px;
    text-decoration:none;
    color:black;
    border-radius:4px;
    transition:all .2s ease;
    display:inline-flex;
    align-items:center;
    gap:4px
}
.btn.show{
    background:#e8f5e9;
    border-color:#42b983;
    color:#42b983
}
.btn.show:hover{
    background:#42b983;
    color:white
}
.btn.edit{
    background:#fff3e0;
    border-color:#ff9800;
    font-size:16px;
    padding:6px 8px
}
.btn.edit:hover{
    background:#ff9800;
    color:white
}
.btn.delete{
    background:#ffebee;
    border-color:#f44336;
    font-size:16px;
    padding:6px 8px
}
.btn.delete:hover{
    background:#f44336;
    color:white
}
.btn.primary{
    background:#42b983;
    color:white;
    border:none
}
.btn.primary:hover{
    background:#35956f;
    transform:translateY(-2px);
    box-shadow:0 4px 12px rgba(66,185,131,.3)
}
.btn.secondary{
    background:#f0f0f0;
    color:#333
}
.btn.secondary:hover{background:#e0e0e0}
/* Floating Add Button */
.floating-add{
    background:#42b983;
    color:white;
    border:none;
    padding:12px 20px;
    border-radius:8px;
    cursor:pointer;
    font-weight:500;
    font-size:14px;
    transition:all .2s ease;
    box-shadow:0 4px 12px rgba(66,185,131,.3)
}
.floating-add:hover{
    background:#35956f;
    transform:translateY(-2px);
    box-shadow:0 6px 16px rgba(66,185,131,.4)
}
/* Modal */
.modal-overlay{
    position:fixed;
    inset:0;
    background:rgba(0,0,0,.5);
    display:flex;
    align-items:center;
    justify-content:center;
    z-index:50;
    animation:fadeIn .2s ease
}
@keyframes fadeIn{
    from{opacity:0}
    to{opacity:1}
}
.modal{
    background:white;
    padding:0;
    border-radius:12px;
    width:90%;
    max-width:500px;
    box-shadow:0 12px 40px rgba(0,0,0,.2);
    animation:slideUp .3s ease;
    max-height:90vh;
    overflow-y:auto
}
.modal-header{
    display:flex;
    justify-content:space-between;
    align-items:center;
    padding:20px;
    border-bottom:1px solid #f0f0f0;
    background:#f9f9f9
}
.modal-header h3{
    margin:0;
    color:#1a1a1a;
    font-size:18px
}
.close-btn{
    background:none;
    border:none;
    font-size:24px;
    cursor:pointer;
    color:#999;
    padding:0;
    width:32px;
    height:32px;
    display:flex;
    align-items:center;
    justify-content:center;
    transition:color .2s ease
}
.close-btn:hover{color:#333}
.modal-form{padding:20px}
.form-group{margin-bottom:16px}
.form-group label{
    display:block;
    margin-bottom:6px;
    font-weight:500;
    color:#333;
    font-size:13px
}
.form-group input,.form-group textarea{
    width:100%;
    padding:10px 12px;
    border:1px solid #ddd;
    border-radius:4px;
    font-size:14px;
    font-family:inherit;
    transition:border-color .2s ease
}
.form-group input:focus,.form-group textarea:focus{
    outline:none;
    border-color:#42b983;
    box-shadow:0 0 0 3px rgba(66,185,131,.1)
}
.modal-actions{
    display:flex;
    justify-content:flex-end;
    gap:12px;
    padding:1em;
    border-top:1px solid #f0f0f0
}
.modal-actions .delete{font-size:12px}
/* Responsive */
@media (max-width:768px){
    .list-lawyers{padding:12px}
    .header{
        flex-direction:column;
        align-items:flex-start
    }
    h2{font-size:22px}
    .floating-add{width:100%}
    .search-input{font-size:13px}
    .table-container{overflow-x:auto}
    .lawyers-table th,.lawyer-row td{
        padding:10px 12px;
        font-size:13px
    }
    .address-cell{max-width:150px}
    .actions-cell{
        flex-direction:column;
        gap:4px
    }
    .btn{
        width:100%;
        justify-content:center
    }
    .pagination{justify-content:center}
    .modal{width:95%}
}
@media (max-width:480px){
    .list-lawyers{padding:8px}
    h2{font-size:18px}
    .search-box{padding:10px 12px}
    .search-input{font-size:12px}
    .lawyers-table th{
        padding:8px;
        font-size:11px
    }
    .lawyer-row td{
        padding:8px;
        font-size:12px
    }
    .name-cell{
        max-width:150px;
        overflow:hidden;
        text-overflow:ellipsis;
        white-space:nowrap
    }
    .address-cell,.address-head-cell, .service-head-cell,.service-cell{display:none}
    .pagination{
        gap:4px;
        padding:12px;
    }
    .pagination-btn,.page{
        padding:6px 8px;
        font-size:11px;
    }
    .page-input{
        width:50px;
        font-size:11px
    }
    .modal{width:98%}
    .modal-header{padding:16px}
    .modal-header h3{font-size:16px}
    .modal-form{padding:16px}
    .modal-actions{flex-direction:column}
    .btn.primary,.btn.secondary{width:100%}
}
</style>
