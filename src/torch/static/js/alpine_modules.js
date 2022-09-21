document.addEventListener('alpine:init',()=>{
    Alpine.data('collections', () => ({
        collections: [],
        filteredCollections: [],
        open: false,
        formData: {
            name: "",
            code: "",
        },
        search: "",
        selectedCollection: null,
        collectionSaved: false,
        openPage(collectioncode){
            window.open(window.location.href + "/" + collectioncode,"_self")
        },
        init() {
            this.open = false;
            var socket = io();

            socket.on('connect', function() {
                console.log('a user connected');
            });

            this.getCollections();
        },
        getCollections(){
            fetch(`/collections/search`, {
                method: "GET"
              }).then((_res) => {
                _res.json().then(data=>{
                    this.selectedCollection = data[0];
                    this.collections = data;
                    this.filteredCollections = data;
                    
                })
              });
        },
        openModal() {
            this.formData.name = "";
            this.formData.code = "";
            this.open = true;
        },
        submitData(e){
            fetch("/collections", {
                method: "POST",
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(this.formData)
            })
            .then((response) => {               
                if(response.status === 200) {
                    this.open = false;
                    this.getCollections();
                }else{
                    throw new Error ("Collection registration failed");
                }
            }).catch(error=>{
                console.error(error);
                alert("Collection registration failed");
                throw new Error ("Collection registration failed");
            })
        },
        searchCollection() {
            if (this.search === "") {
                this.filteredCollections = this.collections;
            }
            this.filteredCollections = this.collections.filter((item) => {
                return (item.name
                  .toLowerCase()
                  .includes(this.search.toLowerCase()) || 
                  item.code
                  .toLowerCase()
                  .includes(this.search.toLowerCase()));
            });         
        },
        selectCollection(collection){
            this.selectedCollection = collection
        },
        saveCollectionSettings(){
            console.log('saveCollectionSettings',this.selectedCollection);
            
            fetch(`/collections`, {
                method: "POST",
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(this.selectedCollection)
              }).then((_res) => {
                _res.json().then(data=>{
                   console.log('saveCollectionSettings',data);
                   this.collectionSaved = true;
                })
              });
        },
        deleteCollection(id){
            
            if (confirm("Are you sure you want to remove this collection?") == true) {
                
                fetch(`${id}`, {
                  method: "DELETE",
                  body: JSON.stringify({ collectionId: id }),
                }).then((_res) => {
                    if(_res.status == 200)
                        _res.json().then(data=>{
                            
                            if (data.status == 'ok')
                                this.collections.splice(this.collections.map(x=>x.id).indexOf(id),1);
                            else
                                alert(data.statusText)  
                        })
                    else
                        alert(_res.statusText)  
                }).catch(error=>{
                    console.log(error);
                    alert('Failed to remove the collection');
                });
              }
        }
    }));

    Alpine.data('specimens',(collectionid)=>({
        specimens: [],
        filteredSpecimens: [],
        notifications: [],
        open: false,
        search: "",
        loading: false,
        fileCounter: 0,
        uploadingMessage: "Uploading <span id='fileName'></span>",
        openPage(specimenid){
            window.open(window.location.href + "/" + specimenid,"_self")
        },
        init(){
            console.log('specimens init', collectionid);

            this.loading = true;
            this.getSpecimens(collectionid).then(data=>{
                this.specimens = data;
                this.filteredSpecimens = data;
                this.loading = false;
            })

            var socket = io();

            socket.on('connect', function() {
                console.log('a user connected');
            });

            socket.on('notify', (n) => {
                this.loading = true;
                this.getSpecimens(collectionid).then(data=>{
                    data.forEach(x => {
                        if(x.id == n.specimenid){
                            x.progress = n.progress;
                            x.style = "width: " + x.progress + "%"
                        }
                    });
                    this.specimens = data;
                    this.loading = false;
                })

               
            })
        },
        openModal() {
            this.fileCounter = 0;
            document.getElementById("uploadingMessageContainer").style.display="none";
            this.open = true;
        },
        getSpecimens(collectionid){            
            return fetch(`/collections/specimens/${collectionid}`, {
                method: "GET"
              }).then((_res) => {
                return _res.json().then(data=>{
                    
                    data.forEach(x => {
                        x.upload_path = x.upload_path.replace("torch\\","../");
                        x.create_date = (new Date(x.create_date)).toLocaleDateString()
                    });
                    return data;
                })
              });
        },
        searchSpecimen() {
            this.loading = true;
            fetch(`/collections/specimens/${collectionid}?searchString=${this.search}`, {
                method: "GET"
            }).then((_res) => {                
                _res.json().then(data => {
                    this.specimens = data;    
                    this.loading = false;              
                })
            }) 
        },  
        updateCounter(e) {
            this.fileCounter = (this.fileCounter + e);
        },
        deleteSpecimen(id){
            
            if (confirm("Are you sure you want to remove this specimen?") == true) {
                
                fetch(`specimen/${id}`, {
                  method: "DELETE"
                }).then((_res) => {
                    if(_res.status == 200)
                        _res.json().then(data=>{
                            
                            if (data.status == 'ok')
                                this.specimens.splice(this.specimens.map(x=>x.id).indexOf(id),1);
                            else
                                alert(data.statusText)  
                        })
                    else
                        alert(_res.statusText)  
                }).catch(error=>{
                    console.log(error);
                    alert('Failed to remove the specimen');
                });
              }
        }                       
    }));

})
