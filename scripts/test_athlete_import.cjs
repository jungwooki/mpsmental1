const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const ExcelJS=require('exceljs');
const importer=require('./athlete_import.js');
const root=path.resolve(__dirname,'..');
const data=JSON.parse(fs.readFileSync(path.join(root,'index.html'),'utf8').match(/const DATA=(.*);\n/)[1]);
async function main(){
  const workbook=new ExcelJS.Workbook();
  await workbook.xlsx.readFile(process.argv[2]);
  const first=importer.parseWorkbook(workbook,data.athletes,data.types,'test.xlsx');
  assert.equal(first.total,first.added.length+first.duplicate+first.errors.length);
  const second=importer.parseWorkbook(workbook,[...data.athletes,...first.added],data.types,'renamed.xlsx');
  assert.equal(second.added.length,0,'same or renamed file must be idempotent');
  const all=importer.parseWorkbook(workbook,[],data.types,'test.xlsx');
  let compared=0;
  for(const a of all.added){
    const old=data.athletes.find(b=>importer.key(a)===importer.key(b)&&a.date===b.date);
    if(!old)continue;
    for(const [name,value] of Object.entries(old.raw))assert.equal(a.raw[name],value);
    assert.equal(a.type,old.type);assert.deepEqual(a.near,old.near);
    for(const axis of ['P','R','I'])assert.ok(Math.abs(a.axes[axis]-old.axes[axis])<1e-10);
    assert.equal(a.growth.stage,old.growth.stage);assert.equal(a.growth.delayed,old.growth.delayed);
    assert.ok(Math.abs(a.growth.chronologicalMonths-old.growth.chronologicalMonths)<1e-8);
    compared++;
  }
  assert.ok(compared>0,'compare scoring against previously generated source records');
  assert.equal(importer.date('2014-02-31'),'');assert.equal(importer.date('2014.2.3'),'2014-02-03');
  assert.equal(importer.date(25569),'1970-01-01');assert.equal(importer.date(0,true),'1904-01-01');
  const mini=new ExcelJS.Workbook(),sheet=mini.addWorksheet('선수');
  const source=workbook.worksheets[0],headers=source.getRow(3).values;
  sheet.addRow(headers);
  const validRow=all.added[0].source.row,values=source.getRow(validRow).values.slice();
  values[1]='테스트 선수';values[5]='TEST-UNIQUE';sheet.addRow(values);
  const latest=values.slice();latest[4]='2026-10-01';sheet.addRow(latest);
  const invalid=values.slice();invalid[1]='누락 테스트';invalid[11]='';sheet.addRow(invalid);
  const otherBirth=values.slice();otherBirth[3]='2013-01-01';sheet.addRow(otherBirth);
  const test=importer.parseWorkbook(mini,[],data.types,'synthetic.xlsx');
  assert.equal(test.added.length,2,'same name with different birth is distinct');
  assert.equal(test.duplicate,1);assert.equal(test.errors.length,1);
  assert.equal(test.added.find(a=>a.birth===importer.date(values[3])).date,'2026-10-01');
  assert.equal(importer.parseWorkbook(mini,test.added,data.types,'again.xlsx').added.length,0);
  const blank=new ExcelJS.Workbook();blank.addWorksheet('잘못된 양식').addRow(['선수명']);
  assert.throws(()=>importer.parseWorkbook(blank,[],data.types,'bad.xlsx'),/양식/);
  console.log(JSON.stringify({passed:true,existing:data.athletes.length,sourceRows:first.total,added:first.added.length,duplicate:first.duplicate,invalid:first.errors.length,scoreParityRecords:compared}));
}
main().catch(e=>{console.error(e);process.exitCode=1;});
