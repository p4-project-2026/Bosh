# 📘 Simple Documentation for the Language Grammar

This document explains the structure and meaning of each construct in your grammar.  
It is organized by **program structure**, **statements**, **expressions**, **operators**, and **literals**.

---

## 🧱 Program Structure

### **Program**
A program consists of a single **block**.

### **Block**
A block is one or more statements separated by newlines or dots:

```
stmt
stmt
stmt
```

or

```
stmt. stmt. stmt
```

Blocks may also appear inside `{ ... }` via **in_code_block**.

---

## 🧾 Statements

There are three categories:

- General statements  
- Definition statements  
- Domain statements  

---

# 1️⃣ General Statements

### **If / Else**
```
if <expr>:
    <block>
~ else:
    <block>
```

Or inline fallback:
```
stmt else stmt
```

### **For All / For Each**
```
for all X in expr:
    <block>
```

### **Repeat Until**
```
repeat until expr:
    <block>
```

### **Count Loop**
```
count i from 1 to 10:
    <block>
```

### **Stop / Quit**
Ends execution.

### **Print**
```
say expr
print expr
output expr
```

### **Return**
```
return
return expr
```

### **Continue / Break**
Loop control.

### **List Assignment**
```
term at index expr is expr
```

### **Insert Into List**
```
append expr to list
prepend expr to list
insert expr to list at index expr
```

### **Remove From List**
```
remove expr from list
remove index expr from list
```

### **Call Function**
```
run Func using (arg1, arg2)
call Func
```

---

# 2️⃣ Definition Statements

### **Variable Assignment**
```
X is expr
```

### **Typed Assignment**
```
X is a TYPE
X is a TYPE expr
```

### **Function / Task Definition**
```
task MyFunc uses(a, b):
{
    block
}
```

---

# 3️⃣ Domain Statements

These look like file‑system or automation commands.

### **Make / Create**
```
make new file expr
create folder expr in expr
```

### **Navigation**
```
go to expr
go up
```

### **Rename / Delete / Copy / Move**
```
rename expr to expr
delete expr
copy from expr to expr
move expr to expr
```

### **Write / Execute / Pause / Wait**
```
write expr to expr
execute expr
pause
wait expr
```

---

# 🧮 Expressions

Expressions follow standard precedence:

1. or  
2. and  
3. equality  
4. relational  
5. addition/subtraction  
6. multiplication/division  
7. unary  
8. power  
9. access  
10. term  

---

## 🔤 Operators & Special Forms

### **Boolean Operators**
- `A or B`
- `A and B`
- `not A`

### **Equality**
- `==`, `equals`, `is`
- `!=`, `not equals`, `is not`
- `is a TYPE`
- `is not a TYPE`

### **Relational**
- `>`, `greater than`
- `<`, `less than`
- `>=`, `greater or equal than`
- `<=`, `less or equal than`

### **String / Pattern**
- `regex`
- `starts with`
- `ends with`
- `contains`

### **Math**
- `+`, `plus`
- `-`, `minus`
- `*`, `times`
- `/`, `divided by`
- `%`, `mod`
- `^`, `pow`, `to the power of`
- `sqrt`, `square root of`
- `floor of`
- `ceiling of`
- `round of`

---

# 📚 Access Expressions

### **List Index**
```
list at index i
```

### **Text Index**
```
letter i of text
```

### **Length**
```
length of term
```

### **First / Last**
```
first of list
last of list
```

### **File Attributes**
```
expr age
expr name
```

### **Unit Conversion**
```
expr seconds
expr days
expr years
```

### **Type Cast**
```
expr as TYPE
```

### **Random**
```
random from expr to expr
```

### **Read**
```
read expr
```

### **List Files**
```
list files in expr
```

### **Text Slice**
```
slice text X from A to B
```

### **Text Cut**
```
cut text X from start at N
cut text X from end at N
```

### **Split**
```
split text X with expr
```

---

# 🧱 Terms & Literals

### **Function Call**
```
Func result using (args)
```

### **Text**
```
"hello {expr}"
```

### **Date**
```
t2024-01-01 12:00:00
```

### **Numbers**
- NUMBER  
- FLOAT  

### **Boolean**
- `true`, `false`

### **List**
```
[1, 2, 3]
```

### **Input**
```
input
input(expr)
```

### **Null**
```
null
```

### **Now / Here**
```
now
now date
here
```

### **Parentheses**
```
(expr)
```

### **Types**
```
text, int, float, boolean, list, date, time
```
