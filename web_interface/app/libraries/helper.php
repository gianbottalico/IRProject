<?php

class Helper {
	public static function parseNumber($input) {
		if (empty($input)) return null;
		if (strstr($input, "/") !== false) {
			$splitters = explode("/", $input);
			if (count($splitters) != 2) return null;
			$a = self::parseNumber($splitters[0]);
			$b = self::parseNumber($splitters[1]);
			if ($b == 0) return null;
			return $a / $b;
		} elseif (is_numeric($input)) {
			return (float)$input;
		} else {
			return null;
		}
	}
}
