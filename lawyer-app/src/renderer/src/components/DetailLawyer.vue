<template>
  <div class="message">
    <p class="error" v-if="error != ''">{{error}}</p>
    <p class="success" v-if="success != ''">{{success}}</p>
  </div>
  <div class="lawyer-detail">
    <button class="btn back" @click="goBack">← Retour à la liste</button>
    <p class="loadText" v-if="loading">Chargement en cours</p>
    <div class="detail-card" v-else>
      <div class="card-header">
        <h1>{{lawyer.title}}</h1>
      </div>
      <div class="contact-section">
        <h3>📞 Coordonnées</h3>
        <div class="contact-grid">
          <div v-if="lawyer.contact?.phone" class="contact-item">
            <span class="contact-icon">☎️</span>
            <div>
              <p class="contact-label">Téléphone</p>
              <a :href="`tel:${lawyer.contact.phone}`" class="contact-value">{{lawyer.contact.phone}}</a>
            </div>
          </div>
          <div v-if="lawyer.contact?.email" class="contact-item">
            <span class="contact-icon">✉️</span>
            <div>
              <p class="contact-label">Email</p>
              <a :href="`mailto:${lawyer.contact.email}`" class="contact-value">{{lawyer.contact.email}}</a>
            </div>
          </div>
          <div v-if="lawyer.contact?.fax" class="contact-item">
            <span class="contact-icon">📠</span>
            <div>
              <p class="contact-label">Fax</p>
              <p class="contact-value">{{lawyer.contact.fax}}</p>
            </div>
          </div>
          <div v-if="lawyer.contact?.site" class="contact-item">
            <span class="contact-icon">🌐</span>
            <div>
              <p class="contact-label">Site Web</p>
              <a :href="lawyer.contact.site" target="_blank" rel="noopener" class="contact-value">{{lawyer.contact.site }}</a>
            </div>
          </div>
          <div v-if="!lawyer.contact?.fax && !lawyer.contact?.email && !lawyer.contact?.site && !lawyer.contact?.phone">
            <p>Aucun coordonnées n'a été sauvegarder</p>
          </div>
        </div>
      </div>
      <div class="address-section">
        <h3>📍 Adresse</h3>
        <p class="address-text">{{lawyer.address}}</p>
      </div>
      <div class="service-section">
        <h3>📜 Prestation de serment</h3>
        <p class="service-date">{{lawyer.service}}</p>
      </div>
      <div class="actions">
        <button class="btn primary" @click="openEditModal">✏️ Modifier</button>
        <button class="btn danger" @click="confirmDelete">🗑️ Supprimer</button>
      </div>
    </div>
    <!-- Modal for Edit -->
    <div v-if="showModal" class="modal-overlay" @click.self="closeModal">
      <div class="modal">
        <div class="modal-header">
          <h3>✏️ Modifier l'avocat</h3>
          <button class="close-btn" @click="closeModal">✕</button>
        </div>
        <form @submit.prevent="saveLawyer" class="modal-form">
          <div class="form-group">
            <label for="title">Nom *</label>
            <input name="title" id="title" v-model="form.title" type="text" placeholder="Nom complet" />
            <p class="inputError" v-if="errorInput?.title">{{errorInput.title}}</p>
          </div>
          <div class="form-group">
            <label for="phone">Téléphone</label>
            <input name="phone" id="phone" v-model="form.contact.phone" type="tel" placeholder="+33 1 23 45 67 89" />
          </div>
          <div class="form-group">
            <label for="email">Email</label>
            <input id="email" name="email" v-model="form.contact.email" type="email" placeholder="email@example.com" />
          </div>
          <div class="form-group">
            <label for="fax">Fax</label>
            <input id="fax" name="fax" v-model="form.contact.fax" type="tel" placeholder="+33 1 23 45 67 89" />
          </div>
          <div class="form-group">
            <label for="site">Site web</label>
            <input name="site" id="site" v-model="form.contact.site" type="url" placeholder="https://example.com" />
          </div>
          <div class="form-group">
            <label for="service">Prestation de serment</label>
            <p class="inputError" v-if="errorInput?.service">{{errorInput.service}}</p>
            <input id="service" name="service" v-model="form.service" type="text" />
          </div>
          <div class="form-group">
            <label for="address">Adresse *</label>
            <p class="inputError" v-if="errorInput?.address">{{errorInput.address}}</p>
            <textarea name="address" id="address" v-model="form.address" type="text" required placeholder="Adresse complète" rows="3"></textarea>
          </div>
          <div class="modal-actions">
            <button type="button" class="btn secondary" @click="closeModal">Annuler</button>
            <button type="submit" class="btn primary">Enregistrer les modifications</button>
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
import{useRouter,useRoute}from 'vue-router'
import * as v from 'valibot'
const showDeleteConfirm = ref(false),
  lawyerToDelete = ref(null),
  router = useRouter(),
  route = useRoute(),
  lawyer = ref(),
  errorInput = ref({}),
  loading = ref(true),
  error = ref(""),
  success = ref(""),
  showModal = ref(false),
  form = ref({
    title:'',
    contact:{phone:'',email:'',fax:'',site:''},
    address:'',
    service:''
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
onMounted(async () =>{
  const id = route.params.id
  try{
    lawyer.value = await window.electronAPI.getOneLawyer(id);
    loading.value = false;
  }catch (error){
    console.error('Erreur lors du chargement:',error)
  }
})
function goBack(){router.back()}
function openEditModal(){
  form.value = JSON.parse(JSON.stringify(lawyer.value))
  showModal.value = true
}
function closeModal(){showModal.value = false}
async function saveLawyer(){
  error.value = "";
  success.value = "";
  const validationResult = v.safeParse(lawyerSchema,form.value);
  errorInput.value ={};
  if (!validationResult.success){
    validationResult.issues.map(issue =>{
      errorInput.value[issue.path[0].key] = issue.message
    })
    return;
  }
  try{
    await window.electronAPI.updateLawyer(lawyer.value._id,JSON.parse(JSON.stringify(form.value)))
    lawyer.value = form.value;
    success.value = "Modification de l'avocat " + lawyer.value.title + " a été effectué avec succès."
    closeModal()
  }catch (error){
    console.error('Erreur lors de la sauvegarde:',error)
    error.value = "Erreur lors de la sauvegarde de l'avocat"
  }
}
/*async function confirmDelete(){
  if(!confirm(`Êtes-vous sûr de vouloir supprimer ${lawyer.value.title}?`)) return
  try{
    await window.electronAPI.deleteLawyer(lawyer.value._id)
    router.push('/')
  }catch (error){
    console.error('Erreur lors de la suppression:',error)
  }
}*/
function confirmDelete(){
    lawyerToDelete.value = lawyer.value;
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
        router.push('/')
    }catch(err){
        console.error("Erreur lors de la suppression", err);
        error.value = "Erreur lors de la suppression de l'avocat";
    }
}
</script>
<style scoped>
.btn.delete:hover,.message{color:#fff}.back,.btn{display:inline-flex;border:1px solid #ddd;background:#fff}.back,.btn,.detail-card{background:#fff}.message,h1{font-weight:700}.btn,.contact-value{text-decoration:none}.back,.btn,.close-btn{cursor:pointer}.contact-label,.form-group label{text-transform:uppercase;letter-spacing:.5px}*{box-sizing:border-box}.message{position:fixed;bottom:0;z-index:1000;left:0;width:100%}.confirm-modal{max-width:400px}.modal-body{padding:1em;text-align:center;color:#000}.modal-actions .delete{font-size:12px}.btn{color:#000;align-items:center;gap:4px}.back,h3{align-items:center;gap:8px}.btn.delete{background:#ffebee;border-color:#f44336;font-size:16px;padding:6px 8px}.btn.delete:hover,.message .error{background:#f44336}.inputError{color:red;font-size:.8em}.message p{padding:.8em 2em;width:100%;opacity:0;animation-name:hiddenMessage;animation-duration:5s;animation-timing-function:ease;text-align:center}.message .success{background:#42b983}.lawyer-detail{padding:20px;min-height:100vh}.loadText{color:#000}.back{margin-bottom:24px;padding:10px 16px;color:#333;border-radius:6px;font-size:14px;font-weight:500;transition:.2s}.back:hover{background:#f5f5f5;border-color:#42b983;transform:translateX(-4px)}.detail-card{border-radius:12px;box-shadow:0 8px 24px rgba(0,0,0,.12);max-width:900px;margin:0 auto;animation:.3s slideUp;overflow:hidden}@keyframes slideUp{from{opacity:0;transform:translateY(20px)}to{opacity:1;transform:translateY(0)}}@keyframes hiddenMessage{0%,100%{opacity:0}20%,80%{opacity:1}}.card-header{background:linear-gradient(135deg,#42b983 0,#35956f 100%);padding:32px;color:#fff;border-bottom:4px solid #2d6a52}.address-text,.contact-item{background:#f9f9f9;border-radius:8px;border-left:4px solid #42b983}h1{margin:0;font-size:32px;word-break:break-word}h3{color:#1a1a1a;font-size:18px;margin:0 0 16px;font-weight:600;display:flex}.address-section,.contact-section,.service-section{padding:24px 32px;border-bottom:1px solid #f0f0f0}.address-section:last-of-type,.contact-section:last-of-type,.service-section:last-of-type{border-bottom:none}.contact-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(250px,1fr));gap:16px}.contact-item{display:flex;gap:12px;padding:12px;transition:.2s}.contact-item:hover{background:#f0f8f5;transform:translateY(-2px);box-shadow:0 4px 12px rgba(66,185,131,.15)}.contact-icon{font-size:24px;display:flex;align-items:center;min-width:30px}.contact-label{margin:0 0 4px;font-size:12px;font-weight:600;color:#999}.contact-value{margin:0;color:#42b983;font-size:15px;font-weight:500;word-break:break-all;transition:color .2s}.contact-value:hover{color:#35956f;text-decoration:underline}.contact-item:hover .contact-value{color:#35956f}.address-text{margin:0;color:#555;font-size:15px;line-height:1.8;padding:16px}.service-date{margin:0;color:#42b983;font-size:16px;font-weight:600;padding:12px 16px;background:#e8f5e9;border-radius:8px;border-left:4px solid #42b983}.actions{display:flex;gap:12px;padding:24px 32px;flex-wrap:wrap}.btn{padding:12px 20px;border:none;border-radius:6px;font-size:14px;font-weight:500;transition:.2s;display:inline-flex;align-items:center;gap:8px}.btn.primary{background:#42b983;color:#fff;flex:1;min-width:180px;justify-content:center}.btn.primary:hover{background:#35956f;transform:translateY(-2px);box-shadow:0 6px 16px rgba(66,185,131,.3)}.btn.danger{background:#ffebee;color:#f44336;border:1px solid #ffcdd2;flex:1;min-width:180px;justify-content:center}.btn.danger:hover{background:#f44336;color:#fff;border-color:#f44336;transform:translateY(-2px);box-shadow:0 6px 16px rgba(244,67,54,.3)}.modal-overlay{position:fixed;inset:0;background:rgba(0,0,0,.5);display:flex;align-items:center;justify-content:center;z-index:50;animation:.2s fadeIn}@keyframes fadeIn{from{opacity:0}to{opacity:1}}.modal{background:#fff;padding:0;border-radius:12px;width:90%;max-width:500px;box-shadow:0 12px 40px rgba(0,0,0,.2);animation:.3s slideUp;max-height:90vh;overflow-y:auto}.modal-header{display:flex;justify-content:space-between;align-items:center;padding:20px;border-bottom:1px solid #f0f0f0;background:linear-gradient(135deg,#42b983 0,#35956f 100%)}.modal-header h3{margin:0;color:#fff;font-size:18px}.close-btn{background:0 0;border:none;font-size:24px;color:#fff;padding:0;width:32px;height:32px;display:flex;align-items:center;justify-content:center;transition:.2s}.close-btn:hover{background:rgba(255,255,255,.2);border-radius:4px}.modal-form{padding:20px}.form-group{margin-bottom:16px}.form-group label{display:block;margin-bottom:6px;font-weight:600;color:#1a1a1a;font-size:13px}.form-group input,.form-group textarea{width:100%;padding:10px 12px;border:1px solid #ddd;border-radius:6px;font-size:14px;font-family:inherit;transition:.2s}.form-group input:focus,.form-group textarea:focus{outline:0;border-color:#42b983;box-shadow:0 0 0 3px rgba(66,185,131,.1)}.modal-actions{display:flex;justify-content:flex-end;gap:12px;padding:1em;border-top:1px solid #f0f0f0}.btn.secondary{background:#f0f0f0;color:#333;padding:10px 16px}.btn.secondary:hover{background:#e0e0e0}@media (max-width:768px){.lawyer-detail{padding:12px}.card-header{padding:20px}.actions,.address-section,.contact-section,.service-section{padding:16px 20px}h1{font-size:24px}h3{font-size:16px}.contact-grid{grid-template-columns:1fr}.actions{flex-direction:column}.btn.danger,.btn.primary{width:100%;min-width:unset}.modal{width:95%}}@media (max-width:480px){.back,.btn.primary,.btn.secondary{width:100%}.lawyer-detail{padding:8px}.back{justify-content:center;font-size:12px}.card-header{padding:16px}h1{font-size:18px}.modal-header h3,h3{font-size:14px}.actions,.address-section,.contact-section,.service-section{padding:12px 16px}.contact-item{padding:10px;font-size:13px}.contact-icon{font-size:20px}.contact-value{font-size:13px}.address-text,.service-date{font-size:13px;padding:12px}.btn{padding:10px 16px;font-size:12px}.modal{width:98%}.modal-form,.modal-header{padding:12px}.modal-actions{flex-direction:column}}</style>