const xlsx = require('node-xlsx')
const jieba = require('nodejieba');
const fs = require('fs');


const excelFilePath = './temp.csv'

const sheets = xlsx.parse(excelFilePath);

console.log(sheets.length);
const sheet = sheets[0];
console.log('sheet', sheet.data[10]);
console.log('length', sheet.data.length);

const myRawMsgList = []
const herRawMsgList = []

sheet.data.forEach(([localId, TalkerId, Type, SubType, IsSender, CreateTime, Status, StrContent, StrTime, Remark, NickName, Sender]) => {
    if (!StrContent) return;
    if (['http', '<msg>', '撤回了一条', '['].some(str => StrContent.includes(str))) return
    const jiebaStr = jieba.cutForSearch(StrContent)
    if (IsSender === '0') { myRawMsgList.push(jiebaStr) } else { herRawMsgList.push(jiebaStr) }
})



const myMsgMap = Array.from(myRawMsgList.flat().reduce((pre, cur) => {
    if (pre.has(cur)) pre.set(cur, pre.get(cur) + 1)
    else pre.set(cur, 1)
    return pre
}, new Map()).entries()).sort(([key, val], [key2, val2]) => val2 - val).map(([key, val]) => {
    return { name: key, value: val }
})
const herMsgMap = Array.from(herRawMsgList.flat().reduce((pre, cur) => {
    if (pre.has(cur)) pre.set(cur, pre.get(cur) + 1)
    else pre.set(cur, 1)
    return pre
}, new Map()).entries()).sort(([key, val], [key2, val2]) => val2 - val).map(([key, val]) => {
    return { name: key, value: val }
})

console.log('myMsgList', Object.prototype.toString.call(myMsgMap), myMsgMap)
console.log('herMsgList', Object.prototype.toString.call(herMsgMap), herMsgMap)

fs.writeFile('myMsgObj.json', JSON.stringify(myMsgMap), 'utf8', (err) => {
    if (err) {
        console.error(err);
    } else {
        console.log('myMsgMap文件写入成功！');
    }
});
fs.writeFile('herMsgObj.json', JSON.stringify(herMsgMap), 'utf8', (err) => {
    if (err) {
        console.error(err);
    } else {
        console.log('herMsgMap文件写入成功！');
    }
})

// const myObj = {}
// const herObj = {}

