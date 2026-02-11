import {contextBridge,ipcRenderer} from 'electron'
import {electronAPI} from '@electron-toolkit/preload'
// Custom APIs for renderer
const api = {}
// Use `contextBridge` APIs to expose Electron APIs to
// renderer only if context isolation is enabled, otherwise
// just add to the DOM global.
if(process.contextIsolated){
  try{
    contextBridge.exposeInMainWorld('electron',electronAPI)
    contextBridge.exposeInMainWorld('api',api)
    contextBridge.exposeInMainWorld('electronAPI',{
      getLawyer:(options) => ipcRenderer.invoke('get-lawyer',options),
      getOneLawyer:(id) => ipcRenderer.invoke('get-one-lawyer', id),
      deleteLawyer:(id) => ipcRenderer.invoke('delete-lawyer', id),
      updateLawyer:(id, data) => ipcRenderer.invoke('update-lawyer',id, data),
      createLawyer:(data) => ipcRenderer.invoke('create-lawyer',data)
    })
  }catch(error){
    console.error(error)
  }
}else{
  window.electron = electronAPI
  window.api = api
}