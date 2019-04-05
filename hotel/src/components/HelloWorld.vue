<template>
  <el-container>
     <el-header direction="vertical" height="50px" style="background-color: rgba(5, 140, 52, 0.75)">
       <div class="head_msg" >
         <b>{{ msg }}</b>
      </div>
      <div class= "login_ico">
        <b>Hi {{ name }}! </b>
        <el-button class="logout" size="small" type="danger" v-on:click="logout()" round>Logout</el-button>
      </div>
    </el-header>
    <el-container>

      <el-main>
  <div>
    <audio id="audio" src="../assets/8472.wav"/>
  <div class="main">
    <el-form :model="ruleForm" status-icon :inline="true" :rules="rules2" ref="ruleForm"  label-width="100px"  size="mini">
        <el-form-item label="酒店  ID" prop="id">
          <el-input v-model="ruleForm.id" placeholder="酒店ID" class="inputstyle"></el-input>
        </el-form-item>
        <el-form-item label="房型  ID" >
          <el-input v-model.number="ruleForm.model" placeholder="房型ID" class="inputstyle"></el-input>
        </el-form-item>
        <el-form-item label="入住日期" class="inputstyle">
            <el-col :span="11">
              <el-date-picker type="date" placeholder="选择日期" v-model="ruleForm.start" class="inputdate"></el-date-picker>
            </el-col>
        </el-form-item>
        <el-form-item label="退房日期" class="inputstyle">
            <el-col :span="11">
              <el-date-picker type="date" placeholder="选择日期" v-model="ruleForm.end"  class="inputdate"></el-date-picker>
            </el-col>
        </el-form-item>

        <el-form-item label="选择平台" class="inputstyle">
          <el-select v-model="ruleForm.region" placeholder="请选择平台" >
            <el-option label="暂不选择" value=""></el-option>
            <el-option label="TAAP" value="TAAP"></el-option>
          </el-select>
        </el-form-item>
       <el-form-item label="备注说明" class="inputstyle">
            <el-input
                type="textarea"
                :autosize="{ minRows: 2, maxRows: 4}"
                placeholder="备注说明"
                v-model="ruleForm.remark"
                class = "inputdate"
            >
            </el-input>
        </el-form-item>
        <br>
        <el-form-item class="inputstyle">
          <el-button type="primary" @click="submitForm(ruleForm)">提交</el-button>
          <el-button @click="resetForm('ruleForm')">清空</el-button>
        </el-form-item>
      </el-form>
    </div>

   <div class="result">
     <div class="resTi">
       <span style="color:#00F">查询结果</span>
       <el-button class="crawler" type="success" @click="crawler()">全部爬取</el-button>
     </div>
    <el-table
    :data="queryData"
    border
    height="500"
    >
    <el-table-column
      label="序号"
      type=index
      width="50">
    </el-table-column>
    <el-table-column
      prop="hotelName"
      label="酒店"
      width="150">
    </el-table-column>

    <el-table-column
      prop="date"
      label="日期"
      width="150">
    </el-table-column>
    <el-table-column
      prop="model"
      label="房型"
      width="150">
    </el-table-column>
    <el-table-column
      prop="bed"
      label="床型"
      width="150">
    </el-table-column>
    <el-table-column
      prop="breakfast"
      label="早餐"
      width="150">
    </el-table-column>
    <el-table-column
      prop="platform"
      label="平台"
      width="150">
    </el-table-column>
    <el-table-column
      prop="price"
      label="价格"
      width="150">
    </el-table-column>
      <el-table-column
      label="房间剩余提示"
      width="150">
        <template slot-scope="scope">
        <el-alert v-if="0 < scope.row.roomLeft <= 5"
          title="房间剩余数不足5间"
          type="error">
        </el-alert>
        <el-alert v-else=""
          title="房间充足"
          type="error">
        </el-alert>
      </template>
    </el-table-column>

  </el-table>
  </div>
  </div>
      </el-main>
    </el-container>
  </el-container>
</template>
<style scoped> @import "../assets/css/login.css" </style>
<script>
    export default {
    data() {
      var validatePass = (rule, value, callback) => {
        if (value === '') {
          callback(new Error('请输入酒店ID'));
        }
      };
      return {
        msg: "酒店价格和存量监控",
        ruleForm: {
          id: '',
          model: '',
          start: '',
          end: "",
          region: "",
          remark: "",
        },
        name: window.sessionStorage.getItem("name"),
        queryData:[],
        rules2: {
          id: [
            { validator: validatePass, trigger: 'blur' }
          ],
        }
      };
    },
    methods: {
      submitForm(formName) {
        if (formName.start !== ""){
           formName.start = this.formatterDate(formName.start)
        }
        if (formName.end !== ""){
           formName.end = this.formatterDate(formName.end)
        }
        if (formName.id !== ""){
          var data = new FormData()
          data.append("hotelId", formName.id)
          data.append("model", formName.model)
          data.append("start", formName.start)
          data.append("end", formName.end)
          data.append("platform", formName.region)
          data.append("username", window.sessionStorage.getItem("user"))
          data.append("remark", formName.remark)
          this.$axios.post(`/hotel/searchHotel`, data
             ).then((response) => {
                 this.queryData = response.data.data
                 this.aplayAudio()
             }).catch((error) => {
                 console.log(error);
             });
        }
      },
      crawler(){
        var data = new FormData()
        data.append("username", window.sessionStorage.getItem("user"))
        this.$axios.post(`/hotel/crawler_all`, data
             ).then((response) => {
                 this.$message({
                      message: "操作成功！",
                      type: 'success',
                  })
             }).catch((error) => {
                 console.log(error);
             });
      },
      logout(){
             window.sessionStorage.removeItem("name");
             window.sessionStorage.removeItem("token");
             window.sessionStorage.removeItem("permissions");
             window.sessionStorage.removeItem("user");
             this.$router.push({path: '/login'})
        },
      aplayAudio (){
        //this.gamemuiscs1 = new Audio("../assets/8472.wav");
        //this.gamemuiscs1.play();
        const audio = document.getElementById('audio');
        audio.muted = true;
        audio.play()
      },
      resetForm(formName) {
        this.$refs[formName].resetFields();
      },
      formatterDate(timestamp) {
            var date = new Date(timestamp);
            var m = date.getMonth() + 1;
            m = m > 9 ? m : "0" + m;
            var d = date.getDate();
            d = d > 9 ? d : "0" + d;
            var h = date.getHours();
            h = h > 9 ? h : "0" + h;
            var M = date.getMinutes();
            M = M > 9 ? M : "0" + M;
            var s = date.getSeconds();
            s = s > 9 ? s : "0" + s;
            return date.getFullYear() + "-" + m + "-" + d;
       },
    }
  }
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
.main{
  top: 0px;
  width: 100%;

}


  .result{
    width: 1251px;
    margin-left: 150px;
    top: 500px;

  }
  .resTi{
    width: 100%;
    margin: 15px;
    font-size: 20px;
    font-family: "Adobe 仿宋 Std R";
  }
  .crawler{
    float: right;
  }
</style>
