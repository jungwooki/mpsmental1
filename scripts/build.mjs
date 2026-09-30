import {mkdir,rm,copyFile,cp,writeFile} from 'node:fs/promises';
await rm('public',{recursive:true,force:true});await mkdir('public',{recursive:true});
await copyFile('index.html','public/index.html');await cp('assets','public/assets',{recursive:true});
for(const name of ['MPS_멘탈포지션_성장통합_A4_3페이지_v4.html','MPS_멘탈포지션_A4_3페이지_리포트_v3.html','MPS_멘탈_통합_유형별_분석.html'])await writeFile('public/'+name,'<!doctype html><html lang="ko"><meta charset="utf-8"><meta http-equiv="refresh" content="0;url=/"><a href="/">최신 멘탈리포트 열기</a></html>');
console.log('Built report application. Private data and source workbooks excluded from static output.');
