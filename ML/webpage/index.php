<html lang = "en">
<head>
  <title>Page</title>
  <meta charset = "UTF-8" />
</head>
<body>
<div id='div1'>
    </div>
    <div id='div2'>
    </div>
    <div>
        <form action="index.php" method="post" autocomplete="off"> <!-- webpage reload -->
            Name: <input type="text" name="name" autofocus><br>
            <input type="submit">
        </form>
    </div>
    
    <script type="text/javascript">
        function show_image(src1, src2) {
            var img1 = document.createElement("img");
            var img2 = document.createElement("img");
            img1.src = src1;
            img2.src = src2;
            var div1 = document.getElementById('div1');
            var div2 = document.getElementById('div2');
            div1.removeChild(div1.firstChild);
            div2.removeChild(div2.firstChild);
            div1.appendChild(img1);
            div2.appendChild(img2);
        }
        //show_image("test/images/58/3.png", "test/images/58/4.png");
    </script>

    <div>
        <?php
        $directory = 'test/images';

        if (isset($_POST["name"])){ #checking if something is in form
            #if yes we add to file
            $folder_name = file_get_contents('test/current.txt');
            $save_path = 'test/images/'.$folder_name.'/info.txt';
            $content = file_get_contents($save_path);
            $content .= $_POST["name"];
            file_put_contents($save_path, $content);

            $cdir = $directory.'/'.$folder_name;
            $current = file_get_contents($cdir.'/counter.txt');
            $next = (int)$current + 1;
            file_put_contents($cdir.'/counter.txt', (string)$next); #rising counter IMPORTANT files must be CHMOD 777
        }

        $scanned_directory = array_diff(scandir($directory), array('..', '.'));
        #print_r($scanned_directory); #list of folders with images
        $processed_file = file_get_contents('test/done.txt');
        $processed = explode("\n", $processed_file);
        #print_r($processed); #list of processed folders
        foreach($scanned_directory as $folder){
            if(in_array($folder, $processed)){ #skipping processed folders
                continue;
            }
            $cdir = $directory.'/'.$folder;
            file_put_contents('test/current.txt', $folder); #saving wich folder is being processed
            $images = array_diff(scandir($cdir), array('..', '.', 'counter.txt')); #list pictures
            natsort($images);
            foreach(array_slice($images, 1) as $image){ #skipping 1 element
                $current = file_get_contents($cdir.'/counter.txt');
                if( (int)substr($image, 0, -4) < (int)$current ){ #skip img we already processed
                    continue;
                }
                $image1 = (int)substr($image, 0, -4) - 1;
                $image1 = (string)$image1;
                echo '<script type="text/javascript">show_image("', $cdir.'/'.$image1.'.png', '", "', $cdir.'/'.$image, '");</script>'; #showing image
                return; #webpage reload - next image
            }
            $processed_file = file_get_contents('test/done.txt');
            $processed_file .= $folder;
            file_put_contents('test/done.txt', $processed_file); #adding folder to file
        }
        ?>
    </div>
</body>
</html>