export const createUserDTO = ({name, email, password, role, storeName, city, phone }) =>{
    if(!name ||!email || !password || !role){
    throw new Error("Campos obrigatórios faltando");
}
return { name, email, password, role, storeName, city, phone };
};