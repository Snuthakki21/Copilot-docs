/** Read a complete selected export, preserving every filename and source byte. */
export async function readUtf8Source(file:File,limit:number):Promise<string>{
 if(file.size>limit)throw Error(`${file.name}: file exceeds ${limit} bytes.`);
 try{return new TextDecoder('utf-8',{fatal:true,ignoreBOM:true}).decode(await file.arrayBuffer());}
 catch{throw Error(`${file.name}: provide a UTF-8 text export; binary or invalid text cannot be analyzed.`);}
}

export async function readSourceFiles(files:File[]):Promise<Record<string,string>>{
 if(files.length>200)throw Error('Maximum 200 files per process.');
 if(files.reduce((total,file)=>total+file.size,0)>8*1024*1024)throw Error('Source export exceeds 8 MiB.');
 // Ordinary objects silently invoke __proto__ instead of retaining that file.
 const result:Record<string,string>=Object.create(null);
 for(const file of files){
  if(Object.hasOwn(result,file.name))throw Error('Duplicate filenames need separate relative paths via API intake.');
  result[file.name]=await readUtf8Source(file,512000);
 }
 return result;
}
