import mongoose from 'mongoose'
export async function connectDB(){
    try{
        await mongoose.connect('mongodb://localhost:27017/lawyer_ddb');
    }catch(error){
        console.error('Erreur mongodb', error);
    }
}