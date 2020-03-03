use rayon::prelude::*;
use std::collections::HashSet;
use std::fs;
use std::io::{self, BufRead, BufReader, Read};

//Creates Vector from file
fn read(io: impl Read) -> io::Result<Vec<Vec<f64>>> {
    let br = BufReader::new(io);
    br.lines()
        .map(|line| {
            line.map(|line| {
                line.split_whitespace()
                    .map(|x| x.parse().unwrap_or(-1.0))
                    .collect()
            })
        })
        .collect()
}

//Compares two objects
fn compare(one: &Vec<Vec<f64>>, two: &Vec<Vec<f64>>, error: f64) -> f64 {
    let length = one.len();
    let mut count: f64 = 0.0;
    let mut seen: HashSet<usize> = HashSet::new();

    for orig in one {
        let size = orig.len();

        for i in 0..length {
            if seen.contains(&i) {
                continue;
            } else {
                let targ = &two[i];

                if (0..size).map(|x| (orig[x] - targ[x]).abs()).sum::<f64>() > error * size as f64 {
                    continue;
                }

                let err_sum = (0..size)
                    .map(|x| 1.0 - (orig[x] - targ[x]).abs())
                    .sum::<f64>();

                count += err_sum / size as f64;
                seen.insert(i);
                break;
            }
        }
    }
    //println!("{:}", count / length as f64);
    count / length as f64
}

//Compares one object with others on different threads
fn one_with_others(
    obj: &(String, Vec<Vec<f64>>),
    dict: &Vec<(String, Vec<Vec<f64>>)>,
) -> Vec<(usize, f64)> {
    let length = dict.len();

    (0..length)
        .into_par_iter()
        .map(|x| {
            println!("Puny human is instructed to wait.. {:}/{:}", x + 1, length);
            (x, compare(&obj.1, &dict[x].1, 0.01))
        })
        .collect()
}

fn main() {
    let ray = 1280; //name of directory
    let obj_cur = "tiguan"; //name of object

    let mut objects = Vec::<(String, Vec<Vec<f64>>)>::new();
    let path_rays = format!("./rays/{:}/", ray);
    let paths = fs::read_dir(path_rays).unwrap();

    let obj_path = format!("./rays/{:}/{:}", ray, obj_cur);
    let obj = (
        obj_cur.to_string(),
        read(fs::File::open(obj_path).unwrap()).unwrap(),
    );

    for path in paths {
        let dir = &path.unwrap().path();
        let name = dir.to_str().unwrap().split("/").last().unwrap();

        objects.push((
            name.to_string(),
            read(fs::File::open(dir).unwrap()).unwrap(),
        ));
    }

    let mut result = one_with_others(&obj, &objects);
    result.sort_by(|a, b| b.1.partial_cmp(&a.1).unwrap());
    print!("{}\n", "_".repeat(200));
    println!("{:}", obj.0);
    for line in result {
        println!(
            "{:>36} |{:<100}| {:<14}",
            objects[line.0].0,
            "▮".repeat((line.1 * 100.0).round() as usize),
            line.1
        );
    }
}
