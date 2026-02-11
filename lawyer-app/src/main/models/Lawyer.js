const mongoose = require('mongoose');
const mongoosePaginate = require('mongoose-paginate-v2')
const LawyerSchema = new mongoose.Schema({
  title: {
    type: String,
    required: true
  },
  service: {
    type: String,
    required: true
  },
  address: {
    type: String,
    required: true
  },
  contact: {
    email: {
      type: String
    },
    phone: {
      type: String
    },
    fax: {
      type: String
    },
    site: {
      type: String
    }
  }
}, { timestamps: true });
LawyerSchema.plugin(mongoosePaginate);


export default mongoose.model('Lawyer', LawyerSchema,'lawyer_ddb');
